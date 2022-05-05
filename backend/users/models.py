'''
from django.contrib.auth.models import AbstractUser
from django.db import models

#import api.models as mods
#mm = mods.Tag
#from api.models import Tag
#from ..api import models as api_models
#mod = api.models.Recipe

class User(AbstractUser):
    pass
    #favorite_recipes = models.ManyToManyField(
    #    api.models.Recipe,
    #    related_name='favorited_by',
    #    verbose_name='Избранные рецепты',
    #    blank=True,
    #)

    @staticmethod
    def get_default_user():
        deleted, _ = User.objects.get_or_create(username='deleted')
        return deleted.pk
'''
