from django.db.models import Sum
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import RecipeBaseSerializer
from .utils.pdf_generator import render_pdf


class FavoritesShoppingCartMixin:
    """
    docstring
    """

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorites(self, *args, **kwargs):
        return self.manage_favorites_or_shopping_cart(
            "favorites", *args, **kwargs
        )

    @action(
        methods=["post", "delete"],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, *args, **kwargs):
        return self.manage_favorites_or_shopping_cart(
            "shopping_cart", *args, **kwargs
        )

    def manage_favorites_or_shopping_cart(self, attr_name, *args, **kwargs):
        word_forms = {
            "favorites": "Избранное",
            "shopping_cart": "Корзина",
        }
        user = self.request.user
        attr = getattr(user, attr_name, None)
        if not attr:
            raise ValidationError(
                "Название аргумента attr_name должно соответствовать "
                "атрибуту экземпляра модели User."
            )
        word = word_forms.get(attr_name, "Избранное")
        recipe = self.get_object()
        if self.request.method == "POST":
            if attr.filter(id=recipe.id).exists():
                raise ValidationError(
                    {
                        "Ошибка добавления!": f"Рецепт уже добавлен в раздел "
                                              f"{word} пользователя {user}."
                    }
                )
            attr.add(recipe)
            serializer = RecipeBaseSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if attr.filter(id=recipe.id).exists():
            attr.remove(recipe)
            return Response(
                {"Успешно!": f"Рецепт удален из раздела {word}."},
                status=status.HTTP_200_OK,
            )

        raise ValidationError(
            {
                "Ошибка удаления!": f"Рецепт отсутсвует в разделе {word} "
                                    f"пользователя {user}."
            }
        )

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, *args, **kwargs):
        recipes = self.request.user.shopping_cart
        shopping_cart = (
            recipes.values("ingredients__ingredient__name")
            .order_by("ingredients__ingredient__name")
            .annotate(total=Sum("ingredients__amount"))
        )
        shopping_dict = {}
        for item in shopping_cart:
            ingredient, amount = item.values()
            shopping_dict.update({ingredient: amount})
        return Response(shopping_dict)

    @action(methods=["get"], detail=False)
    def experiment(self, *args, **kwargs):
        user = self.request.user
        recipes = user.shopping_cart
        shopping_cart = (
            recipes.values(
                "ingredients__ingredient__name",
                "ingredients__ingredient__measurement_unit",
            )
            .order_by("ingredients__ingredient__name")
            .annotate(total=Sum("ingredients__amount"))
        )
        shopping_dict = {}
        for item in shopping_cart:
            ingredient, unit, amount = item.values()
            shopping_dict.update({ingredient: str(amount) + " " + unit})
        request = self.request
        data = {"username": user.username, "list": shopping_dict}
        template = "shopping_list2.html"
        return render_pdf(request, data, template)
