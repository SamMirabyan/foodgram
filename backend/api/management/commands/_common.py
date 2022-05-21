import csv

from django.conf import settings
from django.apps import apps

from api.models import Recipe

PATH = settings.BASE_DIR / 'fixtures'
MODELS = ['user', 'tag', 'subscription', 'recipe']


def _get_model(attr: str):
    models = {
        'tags': apps.get_model('api', 'tag'),
        'favorited_by': apps.get_model('api', 'user'),
        'added_to_cart': apps.get_model('api', 'user'),
        'ingredients': apps.get_model('api', 'ingredient'),
    }
    return models.get(attr)

def populate_recipes(file_name):
    with open(PATH / file_name) as file_object:
        csv_file = csv.reader(file_object, delimiter=',')
        current_header = None
        for row in csv_file:
            recipe_id, header, *values = row
            if header != current_header:
                print(f'Заполняем содержимое атрибута {header}')
                current_header = header
            recipe = Recipe.objects.get(id=recipe_id)
            if attr := getattr(recipe, header):
                model = _get_model(header)
                if header == 'ingredients':
                    ingr_ids = values[::2]
                    amounts = values[1::2]
                    for ingr_id, amount in zip(ingr_ids, amounts):
                        instance = model.objects.get_or_create(ingredient_id=ingr_id, amount=amount)
                        attr.add(instance)
                else:
                    for value in values:
                        attr.add(model.objects.get(id=value))


"""
def add_genres():
    '''
    Add genres to titles.
    '''
    file_name = 'genre_title.csv'
    with open(PATH + file_name) as file_object:
        csv_file = csv.reader(file_object, delimiter=',')
        _ = next(csv_file)
        for row in csv_file:
            title = Title.objects.get(id=int(row[1]))
            genre = Genre.objects.get(id=int(row[2]))
            title.genre.add(genre)
"""