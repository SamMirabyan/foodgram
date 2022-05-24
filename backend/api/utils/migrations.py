import csv


def populate_model_from_migration(apps, schema_editor, model_name, file_path):
    """
    Наполняем модель подготовленными данными.
    """
    model = apps.get_model("api", model_name)
    pre_saved_instances = []
    print(f"Загружаем предустановленные данные модели {model_name} ...")
    try:
        with open(file_path) as file_obj:
            csv_file = csv.reader(file_obj, delimiter=",")
            headers = next(csv_file)
            for row in csv_file:
                data = {key: value for key, value in zip(headers, row)}
                instance = model(**data)
                pre_saved_instances.append(instance)
            model.objects.bulk_create(pre_saved_instances)
    except Exception as e:
        print(f"При загрузке данных произошла ошибка: {e}.")
    print(
        f"Загрузка предустановленных данных завершена. "
        f"Модель {model_name} готова к работе"
    )


def reverse_func(apps, schema_editor, model_name):
    model = apps.get_model("api", model_name)
    model.objects.all().delete()
