import pytest

from .test_utils import create_tags

class TestTagApi:

    @pytest.mark.django_db(transaction=True)
    def test_00_tags_not_auth(self, client):
        response = client.get('/api/tags/')
        assert response.status_code != 404, (
            'Страница `/api/tags/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/tags/` без токена авторизации возвращается статус 200'
        )
        data = {}
        post_response = client.post('/api/tags/', data=data)
        assert post_response.status_code == 401, (
            'Проверьте, что при POST запросе `/api/tags/` без токена авторизации возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_01_tags_auth_user(self, user_client):
        get_response = user_client.get('/api/tags/')
        assert get_response.status_code != 404, (
            'Страница `/api/tags/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert get_response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/tags/` авторизованного юзера возвращается статус 200'
        )
        data = {}
        post_response = user_client.post('/api/tags/', data=data)
        assert post_response.status_code == 403, (
            'Проверьте, что при POST запросе `/api/tags/` авторизованного юзера возвращается статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_tag_admin(self, admin_client):
        data = {}
        response = admin_client.post('/api/tags/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/tags/` с не правильными данными возвращает статус 400'
        )
        data = {'name': 'Завтрак', 'slug': 'breakfast', 'color': '#FF00AA'}
        response = admin_client.post('/api/tags/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе `/api/tags/` с правильными данными возвращает статус 201'
        )
        data = {'name': 'Завтрак', 'slug': 'breakfast', 'color': '#FF00AA'}
        response = admin_client.post('/api/tags/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/tags/` нельзя создать 2 жанра с одинаковым `slug`'
        )
        data = {'name': 'Ужин', 'slug': 'supper', 'color': '#11223B'}
        response = admin_client.post('/api/tags/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе `/api/tags/` с правильными данными возвращает статус 201'
        )
        response = admin_client.get('/api/tags/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/tags/` возвращает статус 200'
        )
        data = response.json()
        assert type(data) == list, (
            'Типом возвращаемых данных должен быть список'
        )
        assert len(data) == 2, (
            'Размер возвращаемых данных не правильный'
        )
        assert {'id': 1, 'name': 'Завтрак', 'slug': 'breakfast', 'color': '#FF00AA'} in data, (
            'Значение параметра `results` не правильное'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_tags_delete(self, admin_client):
        tags = create_tags(admin_client)
        response = admin_client.delete(f'/api/tags/{tags[0]["id"]}/')
        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/tags/{id}/` возвращаете статус 204'
        )
        response = admin_client.get('/api/tags/')
        test_data = response.json()
        assert len(test_data) == len(tags) - 1, (
            'Проверьте, что при DELETE запросе `/api/tags/{id}/` удаляете тэг'
        )

        response = admin_client.get(f'/api/tags/{tags[0]["id"]}/')
        assert response.status_code == 404, (
            'Проверьте, что при GET запросе `/api/tags/{id}/` возвращаете статус 404'
        )
