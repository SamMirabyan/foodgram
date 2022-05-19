from django.apps import AppConfig
from django.db.models.signals import post_delete

from .utils.signals import delete_recipe


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # слушаем сигнал post_delete
        # и при каждом удалении рецепта удаляем картинку.
        post_delete.connect(receiver=delete_recipe, sender=self.get_model('recipe'))
