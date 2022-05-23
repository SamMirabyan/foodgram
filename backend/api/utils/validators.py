import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import APIException


def _validate_hex(value: str, exc_type: Exception):
    if isinstance(exc_type, APIException):
        error = {"color": "Ошибка! Задан неверный цветовой код."}
    else:
        error = "Ошибка! Задан неверный цветовой код."
    regexp = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    if not re.fullmatch(regexp, value):
        raise exc_type(error)
    return value


def model_hex_validator(value, exc_type=ValidationError):
    """
    Валидировать значение поля в модели.
    """
    return _validate_hex(value, exc_type)


def _validate_password(password, instance=None):
    try:
        validate_password(password, instance)
    except ValidationError as e:
        raise serializers.ValidationError({'password': e})
    if instance is not None:
        instance.set_password(password)
