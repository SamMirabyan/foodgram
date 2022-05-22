import pytest

from .test_utils import create_ingredients, db_filter_lookup_counter, total_model_counter

class TestIngredientApi:

    @pytest.mark.django_db(transaction=True)
    def test_00_ingredients_not_auth(self, client):
        response = client.get('/api/ingredients/')
        assert response.status_code != 404, (
            'Страница `/api/ingredients/` не найдена, проверьте этот адрес в *urls.py*'
        )
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/ingredients/` без токена авторизации возвращается статус 200'
        )
        get_response_with_search_params = client.get('/api/ingredients/?name=абрикос')
        assert len(get_response_with_search_params.data) == db_filter_lookup_counter('ingredienttype', 'name', 'абрикос'), (
            'Проверьте, что при POST запросе с параметрами поиска возвращается ответ с фильтрацией по параметру'
        )
        data = {}
        post_response = client.post('/api/ingredients/', data=data)
        assert post_response.status_code == 401, (
            'Проверьте, что при POST запросе `/api/ingredients/` без токена авторизации возвращается статус 401'
        )

    @pytest.mark.django_db(transaction=True)
    def test_01_ingredients_auth_user(self, user_client):
        get_response = user_client.get('/api/ingredients/')
        assert get_response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/ingredients/` авторизованного юзера возвращается статус 200'
        )
        data = {}
        post_response = user_client.post('/api/ingredients/', data=data)
        assert post_response.status_code == 403, (
            'Проверьте, что при POST запросе `/api/ingredients/` авторизованного юзера возвращается статус 403'
        )

    @pytest.mark.django_db(transaction=False)
    def test_02_ingredients_admin(self, admin_client):
        data = {}
        response = admin_client.post('/api/ingredients/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/ingredients/` с не правильными данными возвращает статус 400'
        )
        total_ingredients = total_model_counter('ingredienttype')
        data = {'name': 'Выхухоль', 'measurement_unit': 'г'}
        response = admin_client.post('/api/ingredients/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе `/api/ingredients/` с правильными данными возвращает статус 201'
        )
        data = {'name': 'Выхухоль', 'measurement_unit': 'г'}
        response = admin_client.post('/api/ingredients/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе `/api/ingredients/` нельзя создать 2 одинаковых ингредиента'
        )
        data = {'name': 'Лебедя', 'measurement_unit': 'шт'}
        response = admin_client.post('/api/ingredients/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе `/api/ingredients/` с правильными данными возвращает статус 201'
        )
        assert total_model_counter('ingredienttype') == total_ingredients + 2, (
            'Проверьте, что были созданы два новых ингредиента'
        )
        response = admin_client.get(f'/api/ingredients/{total_ingredients+1}/')
        assert {'id': total_ingredients+1, 'name': 'Выхухоль', 'measurement_unit': 'г'} == response.data, (
            'Проверь соответствие атрибутов созданного ингредиента '
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_ingredients_delete(self, admin_client):
        ingredients = create_ingredients(admin_client)
        response = admin_client.delete(f'/api/ingredients/{ingredients[0]["id"]}/')
        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/ingredients/{id}/` возвращаете статус 204'
        )
        response = admin_client.get('/api/ingredients/')
        test_data = response.json()
        assert len(test_data) == len(ingredients) - 1, (
            'Проверьте, что при DELETE запросе `/api/ingredients/{id}/` удаляете тэг'
        )

        response = admin_client.get(f'/api/ingredients/{ingredients[0]["id"]}/')
        assert response.status_code == 404, (
            'Проверьте, что при GET запросе `/api/ingredients/{id}/` возвращаете статус 404'
        )
