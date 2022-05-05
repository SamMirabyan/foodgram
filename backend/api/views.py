from rest_framework.viewsets import ModelViewSet

from .models import IngredientType, Tag
from .serializers import IngredientSerializer, TagSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    #permission_classes = ...


class IngredientViewSet(ModelViewSet):
    queryset = IngredientType.objects.all()
    serializer_class = IngredientSerializer
    #permission_classes = ...