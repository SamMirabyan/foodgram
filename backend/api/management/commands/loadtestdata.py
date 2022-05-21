import csv

from django.apps import apps
from django.core.management.base import BaseCommand

from ._common import MODELS, populate_recipes, PATH


class Command(BaseCommand):
    help = 'Наполнить БД предустановленными данными.'

    def populate_model(self, model_name, *args, **options):
        '''
        Наполнить данными одну модель.
        '''
        model = apps.get_model('api', model_name)
        instances = []
        file_name = model_name + '.csv'
        with open(PATH / file_name) as file_object:
            csv_file = csv.reader(file_object, delimiter=',')
            headers = next(csv_file)
            for row in csv_file:
                data = {key: value for key, value in zip(headers, row)}
                instance = model(**data)
                instances.append(instance)
            model.objects.bulk_create(instances)

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

    def add_attrs_to_recipes(self, *args, **kwargs):
        file_name = 'test.csv'
        success_message = 'Атрибут успешно добавлен к модели Recipe'
        error_message = 'При добавлении атрибута в модель Recipe произошла ошибка!'
        self.stdout.write(self.style.SQL_FIELD('Добавляем атрибуты модели Recipe'))
        try:
            populate_recipes(file_name)
            self.stdout.write(self.style.SUCCESS(success_message))
        except Exception as e:
            self.stderr.write(self.style.ERROR(error_message))
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
        self.add_attrs_to_recipes()
        # self.add_genres_to_titles()
