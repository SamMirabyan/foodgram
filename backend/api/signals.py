from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Recipe


@receiver(signal=post_delete, sender=Recipe)
def delete_recipe(sender, instance, *args, **kwargs):
    '''
    Удалить картинку вместе с рецептом.
    '''
    instance.image.storage.delete(instance.image.name)
