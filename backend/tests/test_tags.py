import pytest

class TestTagApi:

    @pytest.mark.django_db(transaction=True)
    def test_01_tag_not_auth(self, client):
        response = client.get('/api/tags/')
        assert response.status_code != 404, (
            'Страница `/api/tags/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/tags/` без токена авторизации возвращается статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_02_tag(self, admin_client):
        print(dir(admin_client))
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
    def test_03_genres_delete(self, admin_client):
        genres = create_genre(admin_client)
        response = admin_client.delete(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/v1/genres/{slug}/` возвращаете статус 204'
        )
        response = admin_client.get('/api/v1/genres/')
        test_data = response.json()['results']
        assert len(test_data) == len(genres) - 1, (
            'Проверьте, что при DELETE запросе `/api/v1/genres/{slug}/` удаляете жанр '
        )
        response = admin_client.get(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 405, (
            'Проверьте, что при GET запросе `/api/v1/genres/{slug}/` возвращаете статус 405'
        )
        response = admin_client.patch(f'/api/v1/genres/{genres[0]["slug"]}/')
        assert response.status_code == 405, (
            'Проверьте, что при PATCH запросе `/api/v1/genres/{slug}/` возвращаете статус 405'
        )
