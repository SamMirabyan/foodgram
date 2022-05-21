import django_filters

from api.models import Recipe


CHOICES = (
    (0, False),
    (1, True),
)

class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(method='tag_list_filter')
    is_favorited = django_filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = django_filters.BooleanFilter(method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ['tags', 'author',]

    def tag_list_filter(self, queryset, name, value):
        # queryset = Recipe.objects.all()
        # name = 'tags'
        # value = '1,2'
        value_list = value.split(',')
        return queryset.filter(**{name+'__slug__in': value_list})

    def is_favorited_filter(self, queryset, name, value):
        name = 'favorited_by'
        return self._recipe_field_filter(queryset=queryset, name=name, value=value)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        name = 'added_to_cart'
        return self._recipe_field_filter(queryset=queryset, name=name, value=value)

    def _recipe_field_filter(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated or not value:
            return queryset
        return queryset.filter(**{name: user.id})
