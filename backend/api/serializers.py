from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from . import models as api_models
from .custom_fields import IngredientTypeField, IngredientUnitField

User = get_user_model()


class BaseUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


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
