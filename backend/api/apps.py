from functools import partial

from django.apps import AppConfig
from django.db.models.signals import post_delete, post_migrate

from .signals import delete_recipe, populate_ingredient_type_table


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        post_migrate.connect(partial(populate_ingredient_type_table, model=self.get_model('ingredienttype')), sender=self)
        post_delete.connect(receiver=delete_recipe, sender=self.get_model('recipe'))
