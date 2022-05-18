import csv

from django.apps import apps
from django.core.management.base import BaseCommand

from ._common import MODELS, PATH


class Command(BaseCommand):
    help = 'Наполнить БД предустановленными данными.'

    def populate_model(self, model_name, *args, **options):
        '''
        Наполнить данными одну модель.
        '''
        model = apps.get_model('api', model_name)
        file_name = model_name + '.csv'
        with open(PATH / file_name) as file_object:
            csv_file = csv.reader(file_object, delimiter=',')
            headers = next(csv_file)
            for row in csv_file:
                data = {key: value for key, value in zip(headers, row)}
                model.objects.get_or_create(**data)

    def populate_db(self, *args, **kwargs):
        '''
        Наполнить данными несколько моделей.
        '''
        for model_name in MODELS:
            success_message = 'Данные успешно добавлены в модель {}!'
            error_message = 'При добавлении данных в модель {} произошла ошибка!'
            try:
                self.populate_model(model_name)
                self.stdout.write(self.style.SUCCESS(
                    success_message.format(model_name.title()))
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    error_message.format(model_name.title()))
                )
                print(e)

    # def add_genres_to_titles(self, *args, **kwargs):
    #     success_message = 'Genres added to titles successfully!'
    #     error_message = 'An error occured while adding genres to titles!'
    #     try:
    #         add_genres()
    #         self.stdout.write(self.style.SUCCESS(success_message))
    #     except Exception as e:
    #         self.stderr.write(self.style.ERROR(error_message))
    #         print(e)

    def handle(self, *args, **options):
        self.populate_db()
        # self.add_genres_to_titles()
