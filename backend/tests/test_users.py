import pytest
from django.contrib.auth import get_user_model

from .test_utils import create_users_api
#from .common import auth_client, create_users_api


class Test01UserAPI:
    users_url = '/api/users/'


    @pytest.mark.django_db(transaction=True)
    def test_01_users_not_authenticated(self, client):
        response = client.get(self.users_url)

        assert response.status_code != 404, (
            f'Страница {self.users_url} не найдена, проверьте этот адрес в *urls.py*'
        )

        assert response.status_code == 200, (
            f'Проверьте, что при GET запросе {self.users_url} без токена авторизации возвращается статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_users_username_not_authenticated(self, client, admin):
        response = client.get(f'{self.users_url}{admin.id}/')

        assert response.status_code != 404, (
            f'Страница `{self.users_url}{admin.id}/` не найдена, проверьте этот адрес в *urls.py*'
        )

        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `{self.users_url}{admin.id}/` без токена авторизации возвращается статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_users_me_not_authenticated(self, client):
        response = client.get(f'{self.users_url}me/')

        assert response.status_code != 404, (
            f'Страница `{self.users_url}me/` не найдена, проверьте этот адрес в *urls.py*'
        )

        assert response.status_code == 401, (
            f'Проверьте, что при GET запросе `{self.users_url}me/` без токена авторизации возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_users_get_admin(self, admin_client, admin):
        response = admin_client.get(self.users_url)
        assert response.status_code != 404, (
            'Страница `self.users_url` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            f'Проверьте, что при GET запросе `{self.users_url}` с токеном авторизации возвращается статус 200'
        )
        data = response.json()
        assert 'count' in data, (
            f'Проверьте, что при GET запросе `{self.users_url}` возвращаете данные с пагинацией. '
            'Не найден параметр `count`'
        )
        assert 'next' in data, (
            f'Проверьте, что при GET запросе `{self.users_url}` возвращаете данные с пагинацией. '
            'Не найден параметр `next`'
        )
        assert 'previous' in data, (
            f'Проверьте, что при GET запросе `{self.users_url}` возвращаете данные с пагинацией. '
            'Не найден параметр `previous`'
        )
        assert 'results' in data, (
            f'Проверьте, что при GET запросе `{self.users_url}` возвращаете данные с пагинацией. '
            'Не найден параметр `results`'
        )
        assert data['count'] == 1, (
            f'Проверьте, что при GET запросе `{self.users_url}` возвращаете данные с пагинацией. '
            'Значение параметра `count` не правильное'
        )
        assert type(data['results']) == list, (
            f'Проверьте, что при GET запросе `{self.users_url}` возвращаете данные с пагинацией. '
            'Тип параметра `results` должен быть список'
        )
        assert (
            len(data['results']) == 1
            and data['results'][0].get('username') == admin.username
            and data['results'][0].get('email') == admin.email
        ), (
            f'Проверьте, что при GET запросе `{self.users_url}` возвращаете данные с пагинацией. '
            'Значение параметра `results` не правильное'
        )


    @pytest.mark.django_db(transaction=True)
    def test_07_01_users_username_patch_admin(self, admin_client, admin, user):
        user_1, user_2 = create_users_api(admin_client)
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
        }
        response = admin_client.patch(f'/api/users/{admin.id}/', data=data)
        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/users/{admin.id}/` '
            'с токеном авторизации возвращается статус 200'
        )
        assert admin.first_name == data['first_name'], (
            'Проверьте, что после PATCH запроса данные администратора поменялись'
        )
        assert admin.last_name == data['last_name'], (
            'Проверьте, что после PATCH запроса данные администратора поменялись'
        )

        data = {
            'first_name': 'TestedFirstName',
            'last_name': 'TestedLastName',
        }
        response = admin_client.patch(f'/api/users/{user_1.id}/', data=data)
        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/users/{user_1.id}/` '
            'с токеном авторизации возвращается статус 200'
        )
        user_1.refresh_from_db()
        assert user_1.first_name == data['first_name'], (
            'Проверьте, что после PATCH запроса данные пользователя поменялись'
        )
        assert user.last_name == data['last_name'], (
            'Проверьте, что после PATCH запроса данные пользователя поменялись'
        )
        #test_admin = get_user_model().objects.get(username=admin.username)
        #assert test_admin.first_name == data['first_name'], (
        #    'Проверьте, что при PATCH запросе `/api/v1/users/{username}/` изменяете данные.'
        #)
        #assert test_admin.last_name == data['last_name'], (
        #    'Проверьте, что при PATCH запросе `/api/v1/users/{username}/` изменяете данные.'
        #)
        #response = admin_client.patch(f'/api/v1/users/{user.username}/', data={'role': 'admin'})
        #assert response.status_code == 200, (
        #    'Проверьте, что при PATCH запросе `/api/v1/users/{username}/` '
        #    'от пользователя с ролью admin можно изменить роль пользователя'
        #)
        #response = admin_client.patch(f'/api/v1/users/{user.username}/', data={'role': 'owner'})
        #assert response.status_code == 400, (
        #    'Проверьте, что при PATCH запросе `/api/v1/users/{username}/` '
        #    'от пользователя с ролью admin нельзя назначать произвольные роли пользователя'
        #    'и возвращается стастус 400'
        #)
'''
    @pytest.mark.django_db(transaction=True)
    def test_07_02_users_username_patch_moderator(self, moderator_client, user):
        data = {
            'first_name': 'New USer Firstname',
            'last_name': 'New USer Lastname',
            'bio': 'new user bio'
        }
        response = moderator_client.patch(f'/api/v1/users/{user.username}/', data=data)
        assert response.status_code == 403, (
            'Проверьте, что при PATCH запросе `/api/v1/users/{username}/` '
            'пользователь с ролью moderator не может изменять данные других пользователей'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_03_users_username_patch_user(self, user_client, user):
        data = {
            'first_name': 'New USer Firstname',
            'last_name': 'New USer Lastname',
            'bio': 'new user bio'
        }
        response = user_client.patch(f'/api/v1/users/{user.username}/', data=data)
        assert response.status_code == 403, (
            'Проверьте, что при PATCH запросе `/api/v1/users/{username}/` '
            'пользователь с ролью user не может изменять данные других пользователей'
        )

    @pytest.mark.django_db(transaction=True)
    def test_07_05_users_username_put_user_restricted(self, user_client, user):
        data = {
            'first_name': 'New USer Firstname',
            'last_name': 'New USer Lastname',
            'bio': 'new user bio'
        }
        response = user_client.put(f'/api/v1/users/{user.username}/', data=data)
        code = 403
        assert response.status_code == code, (
            'Проверьте, что PUT запрос на `/api/v1/users/{username}/` '
            f'не доступен и возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_01_users_username_delete_admin(self, admin_client):
        user, moderator = create_users_api(admin_client)
        response = admin_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{username}/` возвращаете статус 204'
        )
        assert get_user_model().objects.count() == 2, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{username}/` удаляете пользователя'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_02_users_username_delete_moderator(self, moderator_client, user):
        users_before = get_user_model().objects.count()
        response = moderator_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{username}/`'
            'не от админа, возвращаете статус 403'
        )
        assert get_user_model().objects.count() == users_before, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{username}/`'
            'не от админа, не удаляете пользователя'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_03_users_username_delete_user(self, user_client, user):
        users_before = get_user_model().objects.count()
        response = user_client.delete(f'/api/v1/users/{user.username}/')
        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{username}/` '
            'не от админа, возвращаете статус 403'
        )
        assert get_user_model().objects.count() == users_before, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{username}/` '
            'не от админа, не удаляете пользователя'
        )

    @pytest.mark.django_db(transaction=True)
    def test_08_04_users_username_delete_superuser(self, user_superuser_client, user):
        users_before = get_user_model().objects.count()
        response = user_superuser_client.delete(f'/api/v1/users/{user.username}/')
        code = 204
        assert response.status_code == code, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{username}/` '
            f'от суперпользователя, возвращаете статус {code}'
        )
        assert get_user_model().objects.count() == users_before - 1, (
            'Проверьте, что при DELETE запросе `/api/v1/users/{username}/` '
            'от суперпользователя, пользователь удаляется.'
        )

    def check_permissions(self, user, user_name, admin):
        client_user = auth_client(user)
        response = client_user.get('/api/v1/users/')
        assert response.status_code == 403, (
            f'Проверьте, что при GET запросе `/api/v1/users/` '
            f'с токеном авторизации {user_name} возвращается статус 403'
        )
        data = {
            'username': 'TestUser9876',
            'role': 'user',
            'email': 'testuser9876@yamdb.fake'
        }
        response = client_user.post('/api/v1/users/', data=data)
        assert response.status_code == 403, (
            f'Проверьте, что при POST запросе `/api/v1/users/` '
            f'с токеном авторизации {user_name} возвращается статус 403'
        )

        response = client_user.get(f'/api/v1/users/{admin.username}/')
        assert response.status_code == 403, (
            f'Проверьте, что при GET запросе `/api/v1/users/{{username}}/` '
            f'с токеном авторизации {user_name} возвращается статус 403'
        )
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = client_user.patch(f'/api/v1/users/{admin.username}/', data=data)
        assert response.status_code == 403, (
            f'Проверьте, что при PATCH запросе `/api/v1/users/{{username}}/` '
            f'с токеном авторизации {user_name} возвращается статус 403'
        )
        response = client_user.delete(f'/api/v1/users/{admin.username}/')
        assert response.status_code == 403, (
            f'Проверьте, что при DELETE запросе `/api/v1/users/{{username}}/` '
            f'с токеном авторизации {user_name} возвращается статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_09_users_check_permissions(self, admin_client, admin):
        user, moderator = create_users_api(admin_client)
        self.check_permissions(user, 'обычного пользователя', admin)
        self.check_permissions(moderator, 'модератора', admin)

    @pytest.mark.django_db(transaction=True)
    def test_10_users_me_get_admin(self, admin_client, admin):
        user, moderator = create_users_api(admin_client)
        response = admin_client.get('/api/v1/users/me/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` от админа, возвращается статус 200'
        )
        response_data = response.json()
        assert response_data.get('username') == admin.username, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете данные пользователя'
        )
        client_user = auth_client(moderator)
        response = client_user.get('/api/v1/users/me/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` с токеном авторизации возвращается статус 200'
        )
        response_data = response.json()
        assert response_data.get('username') == moderator.username, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете данные пользователя'
        )
        assert response_data.get('role') == 'moderator', (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете данные пользователя'
        )
        assert response_data.get('email') == moderator.email, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете данные пользователя'
        )
        assert response_data.get('bio') == moderator.bio, (
            'Проверьте, что при GET запросе `/api/v1/users/me/` возвращаете данные пользователя'
        )
        response = client_user.delete('/api/v1/users/me/')
        assert response.status_code == 405, (
            'Проверьте, что при DELETE запросе `/api/v1/users/me/` возвращается статус 405'
        )

    @pytest.mark.django_db(transaction=True)
    def test_11_01_users_me_patch_admin(self, admin_client):
        user, moderator = create_users_api(admin_client)
        data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'bio': 'description'
        }
        response = admin_client.patch('/api/v1/users/me/', data=data)
        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/v1/users/me/` с токеном авторизации возвращается статус 200'
        )
        response_data = response.json()
        assert response_data.get('bio') == 'description', (
            'Проверьте, что при PATCH запросе `/api/v1/users/me/` изменяете данные'
        )
        client_user = auth_client(moderator)
        response = client_user.patch('/api/v1/users/me/', data={'first_name': 'NewTest'})
        test_moderator = get_user_model().objects.get(username=moderator.username)
        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/v1/users/me/` с токеном авторизации возвращается статус 200'
        )
        assert test_moderator.first_name == 'NewTest', (
            'Проверьте, что при PATCH запросе `/api/v1/users/me/` изменяете данные'
        )

    @pytest.mark.django_db(transaction=True)
    def test_11_02_users_me_patch_user(self, user_client):
        data = {
            'first_name': 'New user first name',
            'last_name': 'New user last name',
            'bio': 'new user bio',
        }
        response = user_client.patch('/api/v1/users/me/', data=data)
        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/v1/users/me/`, '
            'пользователь с ролью user может изменить свои данные, и возвращается статус 200'
        )

        data = {
            'role': 'admin'
        }
        response = user_client.patch('/api/v1/users/me/', data=data)
        response_json = response.json()
        assert response_json.get('role') == 'user', (
            'Проверьте, что при PATCH запросе `/api/v1/users/me/`, '
            'пользователь с ролью user не может сменить себе роль'
        )
'''