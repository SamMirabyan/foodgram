import pytest
from django.contrib.auth import get_user_model

from .test_utils import total_model_counter

User = get_user_model()


class Test00UserRegistration:
    url_signup = '/api/users/'
    url_login = '/api/auth/token/login/'
    url_logout = '/api/auth/token/logout/'
    valid_email = 'valid@hello.fake'
    valid_username = 'valid_username'
    valid_first_name = 'valid'
    valid_last_name = 'username'
    valid_password = 'Test_user'
    valid_data = {
        'email': valid_email,
        'username': valid_username,
        'first_name': valid_first_name,
        'last_name': valid_last_name,
        'password': valid_password,
    }

    @pytest.mark.django_db(transaction=True)
    def test_00_nodata_signup(self, client):
        request_type = 'POST'
        response = client.post(self.url_signup)

        assert response.status_code != 404, (
            f'Страница `{self.url_signup}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` без параметров '
            f'не создается пользователь и возвращается статус {code}'
        )
        response_json = response.json()
        empty_fields = ['email', 'username']
        for field in empty_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что при {request_type} запросе `{self.url_signup}` без параметров '
                f'в ответе есть сообщение о том, какие поля заполенены неправильно'
            )

    @pytest.mark.django_db(transaction=True)
    def test_01_invalid_data_signup(self, client):
        invalid_email = 'invalid_email'
        invalid_password = 'invalid_password@hello.fake'

        invalid_data = {
            'email': invalid_email,
            'username': invalid_password
        }
        request_type = 'POST'
        response = client.post(self.url_signup, data=invalid_data)

        assert response.status_code != 404, (
            f'Страница `{self.url_signup}` не найдена, проверьте этот адрес в *urls.py*'
        )
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с невалидными данными '
            f'не создается пользователь и возвращается статус {code}'
        )

        response_json = response.json()
        invalid_fields = ['email']
        for field in invalid_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что при {request_type} запросе `{self.url_signup}` с невалидными параметрами, '
                f'в ответе есть сообщение о том, какие поля заполенены неправильно'
            )

        valid_email = 'validemail@yamdb.fake'
        invalid_data = {
            'email': valid_email,
        }
        response = client.post(self.url_signup, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` без username '
            f'нельзя создать пользователя и возвращается статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_valid_data_user_signup(self, client):
        total_users_inital = total_model_counter('user')
        request_type = 'POST'
        response = client.post(self.url_signup, data=self.valid_data)
        total_users_after = total_model_counter('user')

        assert response.status_code != 404, (
            f'Страница `{self.url_signup}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )
        assert 'password' not in response.json(), (
            'Проверьте, что в ответе не возвращается пароль.'
        )
        user_id = response.json().get('id')
        valid_data = self.valid_data.copy()
        valid_data.pop('password', None)  # удаляем пароль
        valid_data.update({'id': user_id})  # добавляем id
        assert response.json() == valid_data, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )
#
        new_user = User.objects.filter(email=self.valid_email)
        assert new_user.exists(), (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        assert total_users_after == total_users_inital + 1, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с валидными данными, '
            f'пользователь создается в БД'
        )

        new_user.delete()


    @pytest.mark.django_db(transaction=True)
    def test_03_obtain_auth_token(self, client):

        request_type = 'POST'
        response = client.post(self.url_login)
        assert response.status_code != 404, (
            f'Страница `{self.url_login}` не найдена, проверьте этот адрес в *urls.py*'
        )

        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_login}` без параметров, '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'password': 12345
        }
        response = client.post(self.url_login, data=invalid_data)
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_login}` без username, '
            f'возвращается статус {code}'
        )

        invalid_data = {
            'email': 'invalid_password@hello.fake',
            'password': 12345
        }
        response = client.post(self.url_login, data=invalid_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_login}` с несуществующим username, '
            f'возвращается статус {code}'
        )

        response = client.post(self.url_signup, data=self.valid_data)
        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        invalid_data = {
            'email': self.valid_email,
            'password': 12345
        }
        response = client.post(self.url_login, data=invalid_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_login}` с валидным username, '
            f'но невалидным password, возвращается статус {code}'
        )
        valid_data = {
            'email': self.valid_email,
            'password': self.valid_password,
        }
        response = client.post(self.url_login, data=valid_data)
        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_login}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )
        assert 'auth_token' in response.json(), (
            f'Проверьте, что при {request_type} запросе `{self.url_login}` с валидными данными '
            'В ответет присутсвует токен авторизации'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_registration_same_email_restricted(self, client):
        request_type = 'POST'
        response = client.post(self.url_signup, data=self.valid_data)
        code = 201
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` '
            f'можно создать пользователя с валидными данными и возвращается статус {code}'
        )

        duplicate_username_data = self.valid_data.copy()
        duplicate_username_data['email'] = 'anotheremail@hello.fake'
        response = client.post(self.url_signup, data=duplicate_username_data)
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` нельзя создать '
            f'пользователя, username которого уже зарегистрирован и возвращается статус {code}'
        )
        duplicate_email_data = self.valid_data.copy()
        duplicate_email_data['username'] = 'anotherusername'
        response = client.post(self.url_signup, data=duplicate_username_data)
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.url_signup}` нельзя создать '
            f'пользователя, email которого уже зарегистрирован и возвращается статус {code}'
        )
