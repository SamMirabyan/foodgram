# Generated by Django 3.2.9 on 2022-05-29 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-id',)},
        ),
    ]
