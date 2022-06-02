from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models as api_models
from .custom_fields import (Base64ImageField, IngredientIdField,
                            IngredientTypeField, IngredientUnitField)
from .pagination import RecipesLimitPagination
from .utils.validators import _validate_hex, _validate_password

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    """
    Усеченный сериализатор представления пользователя (User)
    для отображения данных в своем профиле.
    """
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
    """
    Сериализатор создания пользователя (User).
    """
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
        """
        Дополнительно валидируем пароль.
        Сохраняем после успешной валидации.
        """
        raw_password = self.validated_data.pop("password", '123')
        _validate_password(raw_password)
        instance = super().save(**kwargs)
        instance.set_password(raw_password)
        instance.save()
        return instance


class UserMainSerializer(BaseUserSerializer):
    """
    Сериализатор представления и обновления пользователя (User).
    """
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
        """
        Валидируем пароль. Сохраняем после успешной валидации.
        """
        if ("username" or "email") in self.initial_data:
            raise serializers.ValidationError("Это поле нельзя изменить!")
        elif password := self.initial_data.get("password"):
            _validate_password(password, instance)
        return super().update(instance, validated_data)


class RecipeBaseSerializer(serializers.ModelSerializer):
    """
    Усеченный серилизатор представления рецептов (Recipe)
    в сериализаторе UserSubscriptionSerializer.
    """
    class Meta:
        model = api_models.Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class UserSubscriptionSerializer(UserMainSerializer):
    """
    Комбинированный сериализатор представления
    пользователей (User) и их подписок (Subscription).
    Также используется 'усеченный' сериалзитор рецептов.
    """
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
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания подписки.
    Для вывода представлений используется UserSubscriptionSerializer.
    """
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
    """
    Сериализатор создания, представления, обновления тэгов (Tag).
    """
    class Meta:
        model = api_models.Tag
        fields = "__all__"

    def validate_color(self, value):
        return _validate_hex(value, serializers.ValidationError)


class IngredientTypeSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания, представления,
    обновления и удаления типов ингредиента (IngredientType).
    """
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
    """
    Сериализатор комбинированного представления
    ингредиента (Ingredient) и его типа (IngredientType).
    """
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


class CreateIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для валидации и сохранения
    ингредиента (Ingredient) при создании рецепта (Recipe).
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=api_models.IngredientType.objects.all()
    )

    class Meta:
        model = api_models.Ingredient
        fields = (
            "id",
            "amount",
        )


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """
    Сериализатор основного представления моедли Recipe.
    """
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
    """
    Сериализатор создания экземпляров модели Recipe.
    """
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = CreateIngredientSerializer(many=True)
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
        self.add_ingredients_to_recipe(instance, ingredients)
        return instance

    def update(self, instance, validated_data):
        if "author" in self.initial_data:
            raise serializers.ValidationError(
                {"author": "Ошибка! Это поле нельзя поменять."}
            )
        # удаляем старое фото, чтобы не засорять хранилище
        instance.image.storage.delete(instance.image.name)
        new_ingredients = validated_data.pop("ingredients")
        instance.ingredients.all().delete()
        self.add_ingredients_to_recipe(instance, new_ingredients)
        return super().update(instance, validated_data)

    def add_ingredients_to_recipe(self, instance, ingredients):
        for item in ingredients:
            ingredient, _ = api_models.Ingredient.objects.get_or_create(
                ingredient=item["id"], amount=item["amount"]
            )
            instance.ingredients.add(ingredient)

    def to_representation(self, instance):
        """
        Возвращаем сериализатор полного представления экземплара
        рецепта в ответе.
        """
        serializer = RecipeReadOnlySerializer(instance)
        serializer.context["request"] = self.context.get("request")
        return serializer.data


class PasswordSerializer(serializers.Serializer):
    """
    Сериализатор для вью смены пароля.
    """
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
