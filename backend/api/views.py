from rest_framework.viewsets import ModelViewSet

from .models import IngredientType, Recipe, Tag
from .serializers import IngredientTypeSerializer, RecipeReadOnlySerializer, TagSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    #permission_classes = ...


class IngredientViewSet(ModelViewSet):
    queryset = IngredientType.objects.all()
    serializer_class = IngredientTypeSerializer
    #permission_classes = ...


class RecipeReadOnlyViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadOnlySerializer
