from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from . import models as api_models
from .custom_fields import IngredientTypeField, IngredientUnitField

User = get_user_model()


class BaseUserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password',)
    
    def save(self, **kwargs):
        raw_password = self.validated_data.get('password')
        instance = super().save(**kwargs)
        instance.set_password(raw_password)
        instance.save()
        return instance


class SubscriptionSerializer(ModelSerializer):
    
    class Meta:
        model = api_models.Subscription
        fields = ('subscriber', 'subscribed_to',)

        validators = (
            serializers.UniqueTogetherValidator(
                queryset=api_models.Subscription.objects.all(),
                fields=('subscriber', 'subscribed_to',)
            ),
        )

    def validate_subscriber(self, value):
        data = self.initial_data
        if data.get('subscriber') == data.get('subscribed_to'):
            raise serializers.ValidationError('Ошибка! Вы пытаетесь подписаться на себя!')
        return value


class TagSerializer(ModelSerializer):
    class Meta:
        model = api_models.Tag
        fields = '__all__'


class IngredientTypeSerializer(ModelSerializer):
    class Meta:
        model = api_models.IngredientType
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    name = IngredientTypeField(source='ingredient', read_only=True)
    measurement_unit = IngredientUnitField(source='ingredient', read_only=True)

    class Meta:
        model = api_models.Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadOnlySerializer(ModelSerializer):
    author = BaseUserSerializer()
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = api_models.Recipe
        exclude = ('favorited_by', 'added_to_cart',)

    def __init__(self, *args, **kwargs):
        '''
        Если пользователь не авторизован,
        то не показываем поля is_favorited и is_in_shopping_cart.
        '''
        if not kwargs.get('context').get('request').user.is_authenticated:
            del self.fields['is_favorited']
            del self.fields['is_in_shopping_cart']
        return super().__init__(*args, **kwargs)

    def get_is_favorited(self, obj: api_models.Recipe) -> bool:
        '''
        Находится ли рецепт в избранных пользователя.
        '''
        return self.context.get('request').user.favorites.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj: api_models.Recipe) -> bool:
        '''
        Находится ли рецепт в корзине пользователя.
        '''
        return self.context.get('request').user.shopping_cart.filter(id=obj.id).exists()


class SimpleIngredientSerializer(ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=api_models.IngredientType.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = api_models.Ingredient
        fields = ('id', 'amount',)


class RecipeCreateUpdateDeleteSerializer(ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = SimpleIngredientSerializer(many=True)

    class Meta:
        model = api_models.Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time', 'author',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        for item in ingredients:
            ingredient = api_models.Ingredient.objects.create(ingredient=item['id'], amount=item['amount'])
            instance.ingredients.add(ingredient)
        return instance


class PasswordSerializer(Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate(self, attrs):
        user = attrs.get('user')
        current = attrs.get('current_password')
        new = attrs.get('new_password')
        if user.check_password(current):
            user.set_password(new)
            user.save()
        else:
            raise serializers.ValidationError('Вы ввели неверный пароль!')
        #return super().validate(attrs)