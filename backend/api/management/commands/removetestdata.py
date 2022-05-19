from django.apps import apps
from django.core.management.base import BaseCommand

from ._common import MODELS


class Command(BaseCommand):
    help = 'Обнулить все модели в БД.'

    def deplete_model(self, model_name: str, *args, **options):
        '''
        Обнулить одну модель.
        '''
        model = apps.get_model('api', model_name)
        model.objects.all().delete()

    def deplete_db(self, *args, **kwargs):
        '''
        Обнулить все модели.
        '''
        success_message = 'Test data for model {} removed successfully!'
        error_message = 'An error occured during deleting data from model {}!'
        for model_name in MODELS:
            try:
                self.deplete_model(model_name)
                self.stdout.write(self.style.SUCCESS(
                    success_message.format(model_name.title()))
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    error_message.format(model_name.title()))
                )
                print(e)

    def handle(self, *args, **options):
        self.deplete_db()
