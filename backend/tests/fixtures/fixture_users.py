import pytest

@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username='TestAdmin', email='testadmin@hello.py', first_name='Admin', last_name='Test', password='1234567', is_staff=True,)


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser', email='testuser@hello.py', first_name='User', last_name='Test', password='1234567',)


@pytest.fixture
def token_admin(admin):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=admin)

    return {
        'access': str(token),
    }


@pytest.fixture
def admin_client(token_admin):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_admin["access"]}')
    return client


@pytest.fixture
def token_user(user):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user)

    return {
        'access': str(token),
    }


@pytest.fixture
def user_client(token_user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user["access"]}')
    return client
