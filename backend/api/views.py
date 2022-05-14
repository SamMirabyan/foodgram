from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from .models import IngredientType, Recipe, Subscription, Tag
from .pagination import PageLimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrStaffOrReadOnly
from .serializers import BaseUserSerializer, IngredientTypeSerializer, PasswordSerializer, RecipeBaseSerializer, RecipeCreateUpdateDeleteSerializer, RecipeReadOnlySerializer, SubscriptionSerializer, TagSerializer, UserMainSerializer, UserSingUpSerializer, UserSubscriptionSerializer


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
    permission_classes = (IsAuthorOrStaffOrReadOnly,)

    def create(self, request, *args, **kwargs):
        # сериализуем и создаем рецепт
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        recipe = serializer.instance

        # в ответе возвращаем уже существующий сериализованный рецепт
        response_serializer = RecipeReadOnlySerializer(recipe)
        response_serializer.context['request'] = request
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # в ответе возвращаем уже существующий сериализованный рецепт
        response_serializer = RecipeReadOnlySerializer(instance)
        response_serializer.context['request'] = request
        return Response(response_serializer.data)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadOnlySerializer
        return RecipeCreateUpdateDeleteSerializer

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorites(self, *args, **kwargs):
        user = self.request.user
        recipe = self.get_object()
        if self.request.method == 'POST':
            if user.favorites.filter(id=recipe.id).exists():
                raise ValidationError({
                    'Ошибка добавления в избранное!':
                    f'Рецепт уже в избранном пользователя {user}.'
                })
            user.favorites.add(recipe)
            serializer = RecipeBaseSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if user.favorites.filter(id=recipe.id).exists():
            user.favorites.remove(recipe)
            return Response({'Успешно!': 'Рецепт удален из списка избранных.'}, status=status.HTTP_200_OK)

        raise ValidationError({
                'Ошибка удаления из избранного!':
                f'Рецепт отсутсвует в избранном пользователя {user}.'
        })

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, *args, **kwargs):
        user = self.request.user
        recipe = self.get_object()
        if self.request.method == 'POST':
            if user.shopping_cart.filter(id=recipe.id).exists():
                raise ValidationError({
                    'Ошибка добавления в корзину!':
                    f'Рецепт уже в корзине пользователя {user}.'
                })
            user.shopping_cart.add(recipe)
            serializer = RecipeBaseSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if user.shopping_cart.filter(id=recipe.id).exists():
            user.shopping_cart.remove(recipe)
            return Response({'Успешно!': 'Рецепт удален из вашей корзины.'}, status=status.HTTP_200_OK)

        raise ValidationError({
                    'Ошибка удаления из корзины!':
                    f'Рецепт отсутсвует в корзине пользователя {user}.'
                })

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
    queryset = User.objects.all().order_by('id') # add order by to avoid UnorderedObjectListWarning
    pagination_class = PageLimitPagination
    #permission_classes = (permissions.IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        #kwargs.setdefault('context', self.get_serializer_context())
        kwargs.update(self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSingUpSerializer
        return UserMainSerializer

    @action(
        methods=['get'], detail=False,
        serializer_class=BaseUserSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    @action(
        methods=['post'], detail=False,
        serializer_class=PasswordSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def set_password(self, *args, **kwargs):
        data = self.request.data
        data['user'] = self.request.user.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response('Пароль успешно изменен!')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'], detail=False,
        serializer_class=UserSubscriptionSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, *args, **kwargs):
        user = self.request.user
        if queryset := user.subscriptions.all().order_by('-id'):
            subscriptions = [user.subscribed_to for user in queryset]
            paginator = PageLimitPagination()
            paginated = paginator.paginate_queryset(subscriptions, request=self.request)
            serializer = self.serializer_class(paginated, many=True)
            serializer.context['request'] = self.request
            return Response(serializer.data)
        return Response('Вы не подписаны ни на одного пользователя')

    @action(
        methods=['post', 'delete'], detail=True,
        serializer_class=UserSubscriptionSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, *args, **kwargs):
        user = self.request.user
        subscribe_to = self.get_object()
        if self.request.method == 'DELETE':
            if subscription := Subscription.objects.filter(subscriber=user, subscribed_to=subscribe_to):
                subscription.delete()
                return Response(f'Подписка на пользователя {subscribe_to} удалена успешно')
            return Response(f'Ошибка удаления: Вы не подписаны на пользователя {subscribe_to}', status=status.HTTP_400_BAD_REQUEST)
        data = {'subscriber': user.id, 'subscribed_to': subscribe_to.id}
        serializer = SubscriptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer = self.serializer_class(subscribe_to)
            serializer.context['request'] = self.request
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

