from django.apps import apps
from django.core.management.base import BaseCommand

from ._common import MODELS


class Command(BaseCommand):
    help = 'Remove all data from models.'

    def deplete_model(self, model_name: str, *args, **options):
        '''
        Remove test data from given model.
        '''
        model = apps.get_model('reviews', model_name.title())
        model.objects.all().delete()

    def deplete_db(self, *args, **kwargs):
        '''
        Remove test data from all models.
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
