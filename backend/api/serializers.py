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

    class Meta:
        model = api_models.Recipe
        exclude = ('favorited_by',)


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
        #print(user, current, new)
        return super().validate(attrs)