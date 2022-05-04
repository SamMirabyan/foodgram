from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class IngredientType(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=32,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Ingredient(models.Model):
    ingredient = models.ForeignKey(
        IngredientType,
        on_delete=models.CASCADE,
        related_name='recipe_amount',
        verbose_name='Ингредиент',
    )
    amount = models.FloatField(verbose_name='Количество')

    def __str__(self):
        return (f'{self.ingredient.name}: {self.amount} '
                f'{self.ingredient.measurement_unit}')


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Название',
    )
    color = models.IntegerField(verbose_name='Цвет')
    slug = models.SlugField(unique=True, verbose_name='Короткое название')

    def __str__(self):
        return f'{self.slug}, цвет {self.color}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,  # сохранить рецепт при удалении юзера
        related_name='recipes',
        default=User.get_default_user,
        verbose_name='Автор'
    )
    name = models.CharField(max_length=128, verbose_name='Название')
    text = models.TextField(max_length=4000, verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
    )
    cooking_time = models.TimeField(verbose_name='Время приготовления')

    def __str__(self):
        return f'{self.name} от {self.author}'
