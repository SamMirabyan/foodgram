# Generated by Django 3.2.9 on 2022-05-07 19:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_subscription'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddField(
            model_name='recipe',
            name='added_to_cart',
            field=models.ManyToManyField(related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Корзина'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, upload_to='recipes/images/', verbose_name='Картинка'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('subscriber', 'subscribed_to'), name='unique_subscriber'),
        ),
    ]
