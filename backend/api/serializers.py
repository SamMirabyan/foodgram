from rest_framework.serializers import ModelSerializer

from . import models as api_models


class TagSerializer(ModelSerializer):
    class Meta:
        model = api_models.Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = api_models.IngredientType
        fields = '__all__'
