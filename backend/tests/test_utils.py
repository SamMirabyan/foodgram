from django.apps import apps
from django.contrib.auth import get_user_model


def create_users_api(admin_client):
    data = {
        'username': 'AdminTestUser',
        'first_name': 'AdminTestName',
        'last_name': 'AdminTestSurname',
        'email': 'testadmin@hello.fake',
        'password': 'Test_admin',
    }
    admin_client.post('/api/users/', data=data)
    user_1 = get_user_model().objects.get(username=data['username'])
    data = {
        'username': 'TestUser',
        'first_name': 'TestFirstName',
        'last_name': 'TestLastNAme',
        'email': 'testmoder@yamdb.fake',
        'password': 'Test_user'
    }
    admin_client.post('/api/users/', data=data)
    user_2 = get_user_model().objects.get(username=data['username'])
    return user_1, user_2


def create_tags(admin_client):
    result = []
    data = {'name': 'Ланч', 'slug': 'lunch', 'color': '#443FFA'}
    request = admin_client.post('/api/tags/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)

    data = {'name': 'Быстрый перекус', 'slug': 'fast', 'color': '#00FF55'}
    request = admin_client.post('/api/tags/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)

    data = {'name': 'Сладкое', 'slug': 'sweet', 'color': '#C35'}
    request = admin_client.post('/api/tags/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)
    return result


def create_ingredients(admin_client):
    result = []
    data = {'name': 'Синий туман', 'measurement_unit': 'мг'}
    request = admin_client.post('/api/ingredients/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)

    data = {'name': 'Боевой утконос', 'measurement_unit': 'шт'}
    request = admin_client.post('/api/ingredients/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)

    data = {'name': 'Жареные гвозди', 'measurement_unit': 'г'}
    request = admin_client.post('/api/ingredients/', data=data)
    data.update({'id': request.data.get('id')})
    result.append(data)
    return result


def _db_filter_lookup(model_name: str, param: str, value: str):
    model = apps.get_model('api', model_name)
    return model.objects.filter(**{param + '__icontains': value})


def db_filter_lookup_counter(model_name: str, param: str, value: str):
    return _db_filter_lookup(model_name, param, value).count()


def total_model_counter(model_name: str):
    model = apps.get_model('api', model_name)
    return model.objects.count()
