import csv
from time import sleep

from django.conf import settings

DEFAULT_INGREDIENTS_CSV_FILE_PATH = settings.BASE_DIR.parent / 'data' / 'ingredients.csv'


def populate_ingredient_type_table(sender, model, **kwargs):
    '''
    Заполняем модель подготовленными данными при первой миграции.
    Также при каждой миграции проверяем наличие хотя бы одной записи
    в таблице.
    '''
    model_name = model._meta.verbose_name or model._meta.model_name
    print(f'Проверка модели {model_name}...')
    if model.objects.count():
        sleep(2)
        print(f'Дополнительных действий не требуется. Модель {model_name} готова к работе.', )
        return
    print('Загружаем предустановленные данные...')
    try:
        with open(DEFAULT_INGREDIENTS_CSV_FILE_PATH) as file_obj:
            csv_file = csv.reader(file_obj, delimiter=',')
            for row in csv_file:
                name, unit = row
                model.objects.create(name=name, measurement_unit=unit)
    except Exception as e:
        print(f'При загрузке данных произошла ошибка: {e}. Проверьте путь до файла.')
    print(f'Загрузка предустановленных данных завершена. Модель {model_name} готова к работе')


def delete_recipe(sender, instance, *args, **kwargs):
    '''
    Удалить картинку вместе с рецептом.
    '''
    instance.image.storage.delete(instance.image.name)
