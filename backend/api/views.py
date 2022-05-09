from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from .models import IngredientType, Recipe, Subscription, Tag
from .serializers import BaseUserSerializer, IngredientTypeSerializer, PasswordSerializer, RecipeReadOnlySerializer, SubscriptionSerializer, TagSerializer


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
        user = User.objects.get(username='bill')
        recipe = self.get_object()
        if self.request.method == 'POST':
            if recipe.favorited_by.filter(username=user.username).exists():
                return Response(f'Ошибка добавления в избранное! Рецепт уже в избранном пользователя {user}', status=status.HTTP_400_BAD_REQUEST)
            recipe.favorited_by.add(user)
            return Response('Рецепт успешно добавлен в избранное', status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            if recipe.favorited_by.filter(username=user.username).exists():
                user.favorites.remove(recipe)
                return Response('Рецепт успешно удален из избранного', status=status.HTTP_202_ACCEPTED)
            return Response(f'Ошибка удаления из избранного! Рецепт отсутсвует в избранном пользователя {user}', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, *args, **kwargs):
        # user = self.request.user - здесь получаем юзера
        #print(self.request.method)
        user = User.objects.get(username='bill')
        recipe = self.get_object()
        if self.request.method == 'POST':
            if recipe.added_to_cart.filter(username=user.username).exists():
                return Response(f'Ошибка добавления в корзину! Рецепт уже в корзине пользователя {user}', status=status.HTTP_400_BAD_REQUEST)
            recipe.added_to_cart.add(user)
            return Response('Рецепт успешно добавлен в корзину', status=status.HTTP_201_CREATED)
        elif self.request.method == 'DELETE':
            if recipe.added_to_cart.filter(username=user.username).exists():
                user.shopping_cart.remove(recipe)
                return Response('Рецепт успешно удален из корзины', status=status.HTTP_202_ACCEPTED)
            return Response(f'Ошибка удаления из корзины! Рецепт отсутсвует в корзине пользователя {user}', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, *args, **kwargs):
        #recipes = self.request.user.shopping_cart
        recipes = User.objects.get(username='bill').shopping_cart
        shopping_cart = recipes.values('ingredients__ingredient__name').order_by('ingredients__ingredient__name').annotate(total=Sum('ingredients__amount'))
        shopping_dict = {}
        for item in shopping_cart:
            ingredient, amount = item.values()
            shopping_dict.update({ingredient: amount})
        return Response(shopping_dict)


class UserReadOnlyViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = BaseUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def me(self, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, serializer_class=PasswordSerializer)
    def set_password(self, *args, **kwargs):
        """
        Можно использовать сериализатор. ПОдумать.
        """
        data = self.request.data
        data['user'] = self.request.user.id
        #current_pass = data.get('current_password')
        #new_pass = data.get('new_password')
        #print(self.request.data)
        #if not (current_pass or new_pass):
        #    error_message = ('Ошибка! Поля "current_password" '
        #                     'и "new_password" обязательны')
        #    return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        #user = self.request.user
        #ser = self.serializer_class(data={'current_password': current_pass, 'new_password': new_pass, 'user': user.id})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response('Пароль успешно изменен!')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #if user.check_password(current_pass):
        #    user.set_password(new_pass)
        #    user.save()
        #    return Response('Пароль успешно изменен')
        #return Response('Неверный пароль!', status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=False)
    def subscriptions(self, *args, **kwargs):
        user = self.request.user
        subscriptions = user.subscriptions.all()
        if subscriptions.exists():
            subscriptions = [user.subscribed_to for user in subscriptions.iterator()]
            serializer = self.serializer_class(subscriptions, many=True)
            return Response(serializer.data)
        return Response('Вы не подписаны ни на одного пользователя')
    
    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, *args, **kwargs):
        user = self.request.user
        subscribe_to = self.get_object()
        if self.request.method == 'DELETE':
            subscription = Subscription.objects.filter(subscriber=user, subscribed_to=subscribe_to)
            if subscription:
                subscription.delete()
                return Response(f'Подписка на пользователя {subscribe_to} удалена успешно')
            return Response(f'Ошибка удаления: Вы не подписаны на пользователя {subscribe_to}', status=status.HTTP_400_BAD_REQUEST)
        data = {'subscriber': user.id, 'subscribed_to': subscribe_to.id}
        serializer = SubscriptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer = self.serializer_class(subscribe_to)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

