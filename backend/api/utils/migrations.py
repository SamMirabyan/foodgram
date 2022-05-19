import csv


def populate_model_from_migration(apps, schema_editor, model_name, file_path):
    '''
    Наполняем модель подготовленными данными.
    '''
    model = apps.get_model('api', model_name)
    ingredients = []
    print(f'Загружаем предустановленные данные модели {model_name} ...')
    try:
        with open(file_path) as file_obj:
            csv_file = csv.reader(file_obj, delimiter=',')
            for row in csv_file:
                name, unit = row
                ingredient = model(name=name, measurement_unit=unit)
                ingredients.append(ingredient)
            model.objects.bulk_create(ingredients)
    except Exception as e:
        print(f'При загрузке данных произошла ошибка: {e}.')
    print(f'Загрузка предустановленных данных завершена. Модель {model_name} готова к работе')


def reverse_func(apps, schema_editor, model_name):
    model = apps.get_model('api', model_name)
    model.objects.all().delete()
