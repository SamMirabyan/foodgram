import base64
from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.serializers import ImageField, RelatedField, ValidationError


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, base64_code = data.split(';base64,')
            try:
                code_file = base64.b64decode(base64_code)
            except Exception as e:
                raise ValidationError({
                    'file': str(e)
                })
            _, file_ext = header.split('/')
            file_name = f'{datetime.now():%Y-%m-%d-%H-%M-%S)}'
            username = self.context.get('request').user.username
            full_name = username + '_' + file_name + '.' + file_ext
            image = SimpleUploadedFile(name=full_name, content=code_file)
            return super(Base64ImageField, self).to_internal_value(image)
        raise ValidationError({'Ошибка!': 'Неверный формат.'})


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


class IngredientIdField(RelatedField):
    """
    Поле для вывода id ингредиента модели IgredientType
    в результат сериализации модели Ingredient.
    """
    def to_representation(self, value):
        return value.id
