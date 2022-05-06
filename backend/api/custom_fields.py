from rest_framework.serializers import RelatedField


class IngredientTypeField(RelatedField):
    """
    Поле для вывода названия ингредиента модели IgredientType
    в результат сериализации модели Ingredient.
    """
    def to_representation(self, value):
        return value.name


class IngredientUnitField(RelatedField):
    """
    Поле для вывода названия ингредиента модели IgredientType
    в результат сериализации модели Ingredient.
    """
    def to_representation(self, value):
        return value.measurement_unit
