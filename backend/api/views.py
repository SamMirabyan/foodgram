from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .mixins import FavoritesShoppingCartMixin
from .models import IngredientType, Recipe, Subscription, Tag
from .pagination import PageLimitPagination
from .permissions import (IsAdminOrReadOnly, IsAuthorOrStaffOrReadOnly,
                          PatchDeleteForAdminOnly)
from .serializers import (BaseUserSerializer, IngredientTypeSerializer,
                          PasswordSerializer, RecipeCreateUpdateSerializer,
                          RecipeReadOnlySerializer, SubscriptionSerializer,
                          TagSerializer, UserMainSerializer,
                          UserSingUpSerializer, UserSubscriptionSerializer)
from .utils.filters import IngredientFilter, RecipeFilter

User = get_user_model()


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ModelViewSet):
    queryset = IngredientType.objects.all()
    serializer_class = IngredientTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet, FavoritesShoppingCartMixin):
    """
    Обработка запросов на эндпоинты `/api/recipes/*`.
    """
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthorOrStaffOrReadOnly,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadOnlySerializer
        return RecipeCreateUpdateSerializer


class UserViewset(ModelViewSet):
    """
    Обработка запросов на эндпоинты `/api/users/*`.
    """
    queryset = User.objects.all().order_by(
        "id"
    )  # add order by to avoid UnorderedObjectListWarning
    pagination_class = PageLimitPagination
    permission_classes = (PatchDeleteForAdminOnly,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserSingUpSerializer
        return UserMainSerializer

    @action(
        methods=["get"],
        detail=False,
        serializer_class=BaseUserSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, *args, **kwargs):
        user = self.request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    @action(
        methods=["post"],
        detail=False,
        serializer_class=PasswordSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def set_password(self, *args, **kwargs):
        data = self.request.data
        data["user"] = self.request.user.id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return Response("Пароль успешно изменен!")

    @action(
        methods=["get"],
        detail=False,
        serializer_class=UserSubscriptionSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, *args, **kwargs):
        user = self.request.user
        if (
            queryset := User.objects.filter(
                **{"subscribers__subscriber": user}).order_by("-id")
        ):
            page = self.paginate_queryset(queryset)
            serializer = self.serializer_class(page, many=True)
            serializer.context["request"] = self.request
            return self.get_paginated_response(serializer.data)
        return Response("Вы не подписаны ни на одного пользователя")

    @action(
        methods=["post", "delete"],
        detail=True,
        serializer_class=UserSubscriptionSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, *args, **kwargs):
        user = self.request.user
        subscribe_to = self.get_object()
        if self.request.method == "DELETE":
            if subscription := Subscription.objects.filter(
                subscriber=user, subscribed_to=subscribe_to
            ):
                subscription.delete()
                return Response(
                    f"Подписка на пользователя {subscribe_to} удалена успешно"
                )
            return Response(
                ("Ошибка удаления: "
                 f"Вы не подписаны на пользователя {subscribe_to}"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {"subscriber": user.id, "subscribed_to": subscribe_to.id}
        serializer = SubscriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.serializer_class(subscribe_to)
        serializer.context["request"] = self.request
        return Response(serializer.data, status=status.HTTP_201_CREATED)
