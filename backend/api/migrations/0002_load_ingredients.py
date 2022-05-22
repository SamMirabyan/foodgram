from functools import partial

from django.conf import settings
from django.db import migrations

from api.utils.migrations import populate_model_from_migration, reverse_func

DEFAULT_INGREDIENTS_CSV_FILE_PATH = (
    settings.BASE_DIR.parent / "data" / "ingredients.csv"
)


class Migration(migrations.Migration):
    """
    Наполнить модель IngredientType подготовленными данными
    при первой миграции.
    """

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            partial(
                populate_model_from_migration,
                model_name="IngredientType",
                file_path=DEFAULT_INGREDIENTS_CSV_FILE_PATH,
            ),
            reverse_func,
        )
    ]
