from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .models import IngredientType, Recipe, Tag
from .serializers import IngredientTypeSerializer, RecipeReadOnlySerializer, TagSerializer


User = get_user_model()

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

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, *args, **kwargs):
        # user = self.request.user - здесь получаем юзера
        #print(self.request.method)
        user = User.objects.last()
        recipe = self.get_object()
        if self.request.method == 'POST':
            if recipe.favorited_by.filter(username=user.username).exists():
                return Response(f'Ошибка добавления в избранное! Рецепт уже в избранном пользователя {user}', status=status.HTTP_400_BAD_REQUEST)
            recipe.favorited_by.add(user)
            print(recipe.favorited_by.all())
            return Response('Рецепт успешно добавлен в избранное', status=status.HTTP_201_CREATED)
        if recipe.favorited_by.filter(username=user.username).exists():
            #recipe.favorited_by.exclude(username=user.username)
            #print(recipe.favorited_by.all())
            return Response('Рецепт успешно удален из избранного', status=status.HTTP_204_NO_CONTENT)
        print(recipe.favorited_by.all())
        return Response(f'Ошибка удаления из избранного! Рецепт отсутсвует в избранном пользователя {user}', status=status.HTTP_400_BAD_REQUEST)
        

        
