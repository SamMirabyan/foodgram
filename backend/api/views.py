from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from .models import IngredientType, Recipe, Subscription, Tag
from .pagination import PageLimitPagination
from .permissions import IsAdminOrReadOnly
from .serializers import BaseUserSerializer, IngredientTypeSerializer, PasswordSerializer, RecipeCreateUpdateDeleteSerializer, RecipeReadOnlySerializer, SubscriptionSerializer, TagSerializer, UserMainSerializer, UserSingUpSerializer

User = get_user_model()


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ModelViewSet):
    queryset = IngredientType.objects.all()
    serializer_class = IngredientTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeReadOnlyViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadOnlySerializer
        return RecipeCreateUpdateDeleteSerializer

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, *args, **kwargs):
        user = self.request.user
        #print(self.request.method)
        #user = User.objects.get(username='bill')
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
        user = self.request.user
        #print(self.request.method)
        #user = User.objects.get(username='bill')
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
    #serializer_class = BaseUserSerializer
    pagination_class = PageLimitPagination
    #permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSingUpSerializer
        return UserMainSerializer

    @action(methods=['get'], detail=False, serializer_class=BaseUserSerializer, permission_classes=[permissions.IsAuthenticated])
    def me(self, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, serializer_class=PasswordSerializer, permission_classes=[permissions.IsAuthenticated])
    def set_password(self, *args, **kwargs):
        data = self.request.data
        data['user'] = self.request.user.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response('Пароль успешно изменен!')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, serializer_class=UserMainSerializer, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, *args, **kwargs):
        user = self.request.user
        subscriptions = user.subscriptions.all()
        if subscriptions.exists():
            subscriptions = [user.subscribed_to for user in subscriptions.iterator()]
            paginator = PageLimitPagination()
            paginated = paginator.paginate_queryset(subscriptions, request=self.request)
            #print(paginated)
            #subscriptions = [user.subscribed_to for user in subscriptions.iterator()]
            #paginator = LimitOffsetPagination()
            #paginated = paginator.paginate_queryset(subscriptions, limit)
            #serializer = UserMainSerializer(paginated, many=True)
            serializer = self.serializer_class(paginated, many=True)
            serializer.context['request'] = self.request
            #serializer = self.serializer_class(paginated, many=True)
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

