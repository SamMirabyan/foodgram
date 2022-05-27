import django_filters

from api.models import IngredientType, Recipe

BOOLEAN_CHOICES = ((0, False), (1, True))


class IngredientFilter(django_filters.FilterSet):
    """
    Для фильтрации ингредиентов по названию (части).
    """
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = IngredientType
        fields = ("name",)


class RecipeFilter(django_filters.FilterSet):
    """
    Для фильтрации рецептов по тэгам,
    и факту нахождения в избранном или корзине.
    """
    tags = django_filters.CharFilter(method="tag_list_filter")
    is_favorited = django_filters.ChoiceFilter(
        choices=BOOLEAN_CHOICES,
        method="is_favorited_filter"
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=BOOLEAN_CHOICES,
        method="is_in_shopping_cart_filter"
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
        )

    def tag_list_filter(self, queryset, name, value):
        """
        Фильтрация по тэгу (допускается несколько).
          - queryset = Recipe.objects.all()
          - name = 'tags'
          - value = '1,2'
        """
        value_list = value.split(",")
        return queryset.filter(**{name + "__slug__in": value_list})

    def is_favorited_filter(self, queryset, name, value):
        """
        Фильтрация по факту нахождения в избранном.
        """
        name = "favorited_by"
        return self._recipe_field_filter(
            queryset=queryset, name=name, value=value
        )

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """
        Фильтрация по факту нахождения в корзине.
        """
        name = "added_to_cart"
        return self._recipe_field_filter(
            queryset=queryset, name=name, value=value
        )

    def _recipe_field_filter(self, queryset, name, value):
        """
        Функция-помощник, прямо не используется.
        """
        user = self.request.user
        print(value)
        if isinstance(value, bool):
            print('fsfsf')
        if not user.is_authenticated or not value:
            return queryset
        return queryset.filter(**{name: user.id})
