from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models as api_models
from .custom_fields import (Base64ImageField, IngredientIdField,
                            IngredientTypeField, IngredientUnitField)
from .pagination import RecipesLimitPagination
from .utils.validators import _validate_hex, _validate_password

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class UserSingUpSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        read_only_fields = ("id",)

    def save(self, **kwargs):
        raw_password = self.validated_data.get("password")
        _validate_password(raw_password)
        instance = super().save(**kwargs)
        instance.set_password(raw_password)
        return instance


class UserMainSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def to_representation(self, instance):
        """
        Если пользователь не авторизован
        или если пользователь видит свой профиль,
        то не показываем поле `is_subscribed`.
        """
        if (
            not self.context.get("request").user.is_authenticated
            or self.context.get("request").user.id == instance.id
        ):
            self.fields.pop("is_subscribed", None)
        return super().to_representation(instance)

    def get_is_subscribed(self, obj):
        return (
            self.context.get("request")
            .user.subscriptions.filter(subscribed_to_id=obj.id)
            .exists()
        )

    def update(self, instance, validated_data):
        if ("username" or "email") in self.initial_data:
            raise serializers.ValidationError("Это поле нельзя изменить!")
        elif password := self.initial_data.get("password"):
            _validate_password(password, instance)
        return super().update(instance, validated_data)


class RecipeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class UserSubscriptionSerializer(UserMainSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserMainSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("recipes",)

    def get_recipes(self, obj):
        """
        Метод получения рецептов пользователя
        с пагинацией.
        """
        request = self.context.get("request")
        queryset = obj.recipes.all().order_by("-id")
        paginator = RecipesLimitPagination()
        paginated = paginator.paginate_queryset(queryset, request)
        serializer = RecipeBaseSerializer(paginated, many=True)
        # return serializer.data
        return paginator.get_paginated_response(serializer.data)

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Subscription
        fields = (
            "subscriber",
            "subscribed_to",
        )

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=api_models.Subscription.objects.all(),
                fields=(
                    "subscriber",
                    "subscribed_to",
                ),
            ),
        )

    def validate_subscriber(self, value):
        data = self.initial_data
        if data.get("subscriber") == data.get("subscribed_to"):
            raise serializers.ValidationError(
                {"subscribed_to": "Ошибка! Вы пытаетесь подписаться на себя!"}
            )
        return value


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Tag
        fields = "__all__"

    def validate_color(self, value):
        return _validate_hex(value, serializers.ValidationError)


class IngredientTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.IngredientType
        fields = "__all__"

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=api_models.IngredientType.objects.all(),
                fields=(
                    "name",
                    "measurement_unit",
                ),
            ),
        )


class IngredientSerializer(serializers.ModelSerializer):
    name = IngredientTypeField(source="ingredient", read_only=True)
    measurement_unit = IngredientUnitField(source="ingredient", read_only=True)
    id = IngredientIdField(source="ingredient", read_only=True)

    class Meta:
        model = api_models.Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class SimpleIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=api_models.IngredientType.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = api_models.Ingredient
        fields = (
            "id",
            "amount",
        )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                {
                    "amount": (
                        "Ошибка! Количество ингедиентов не может "
                        "быть меньше или равно нулю."
                    )
                }
            )
        return value


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    author = UserMainSerializer()
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = api_models.Recipe
        fields = (
            "id",
            "name",
            "text",
            "author",
            "cooking_time",
            "ingredients",
            "image",
            "tags",
            "image",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def to_representation(self, instance):
        """
        Если пользователь не авторизован,
        то не показываем поля is_favorited и is_in_shopping_cart.
        """
        if not self.context.get("request").user.is_authenticated:
            self.fields.pop("is_favorited", None)
            self.fields.pop("is_in_shopping_cart", None)
        return super().to_representation(instance)

    def get_is_favorited(self, obj: api_models.Recipe) -> bool:
        """
        Находится ли рецепт в избранных пользователя.
        """
        return (
            self.context.get("request")
            .user.favorites.filter(id=obj.id)
            .exists()
        )

    def get_is_in_shopping_cart(self, obj: api_models.Recipe) -> bool:
        """
        Находится ли рецепт в корзине пользователя.
        """
        return (
            self.context.get("request")
            .user.shopping_cart.filter(id=obj.id)
            .exists()
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = SimpleIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = api_models.Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )

    def create(self, validated_data):
        """
        DRF по умолчанию не сериализует глубоко вложенные связи моделей.
        Т.к. у нас модель Ingredient связана с моделью IngredientType,
        при получении запроса мы сначала сериализуем именно IngredientType,
        чтобы понять, что такой тип ингредиента существует.

        Если тип ингредиента и его количество прошли валидацию,то мы:
          1. Убираем словарь ingredients валидированных данных.
          2. Создаем экземпляр рецепта без ингредиентов.
          3. По каждому ключу словаря ingredients
             создаем экземпляр класса Ingredient и добавляем
             в соответствующий атрибут экземпляра рецепта.
        """
        ingredients = validated_data.pop("ingredients")
        instance = super().create(validated_data)
        for item in ingredients:
            ingredient = api_models.Ingredient.objects.get_or_create(
                ingredient=item["id"], amount=item["amount"]
            )
            instance.ingredients.add(ingredient)
        return instance

    def update(self, instance, validated_data):
        if "author" in self.initial_data:
            raise serializers.ValidationError(
                {"author": "Ошибка! Это поле нельзя поменять."}
            )
        return super().update(instance, validated_data)

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                {
                    "cooking_time": (
                        "Ошибка! Время приготовления не может "
                        "быть меньше или равно нулю"
                    )
                }
            )
        elif value > 360:
            raise serializers.ValidationError(
                {
                    "cooking_time": (
                        "Ошибка! Вы пытаетесь сохранить рецепт "
                        "со сроком приготовления более 6 часов. "
                        "В данном случае рекомендуется при "
                        "создании указать время, затраченное "
                        "на выполнение основных операций. "
                        "А время на доведение до готовности "
                        "указать в самом описании рецепта."
                    )
                }
            )
        return value

    def to_representation(self, instance):
        """
        Возвращаем сериализатор полного представления экземплара
        рецепта в ответе.
        """
        serializer = RecipeReadOnlySerializer(instance)
        serializer.context["request"] = self.context.get("request")
        return serializer.data


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate(self, attrs):
        user = attrs.get("user")
        current = attrs.get("current_password")
        new = attrs.get("new_password")
        if user.check_password(current):
            _validate_password(new, user)
        else:
            raise serializers.ValidationError("Вы ввели неверный пароль!")
        return super().validate(attrs)
