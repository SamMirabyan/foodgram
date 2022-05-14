from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    '''
    Основной класс юзера
    '''
    email = models.EmailField(_('email address'))
    password = models.CharField(_('password'), max_length=128)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    @staticmethod
    def get_default_user():
        deleted, _ = User.objects.get_or_create(username='deleted')
        return deleted.pk


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
        related_name='recipe_amount',
        on_delete=models.CASCADE,
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
    color = models.CharField(max_length=7, verbose_name='Цвет')
    slug = models.SlugField(unique=True, verbose_name='Короткое название')

    def __str__(self):
        return f'{self.slug}, цвет {self.color}'


class Recipe(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название')
    text = models.TextField(max_length=4000, verbose_name='Описание')
    cooking_time = models.IntegerField(verbose_name='Время приготовления')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка',
        blank=True
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.SET_DEFAULT,  # сохранить рецепт при удалении юзера
        default=User.get_default_user,
        verbose_name='Автор'
    )
    favorited_by = models.ManyToManyField(
        User,
        related_name='favorites',
        verbose_name='Избранное',
    )
    added_to_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart',
        verbose_name='Корзина',
    )
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

    def __str__(self):
        return f'{self.name} от {self.author}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE,
        verbose_name='Подписки',
    )
    subscribed_to = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='Подписчики',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed_to'],
                name='unique_subscriber'
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f'{self.subscriber} подписался на {self.subscribed_to}'
