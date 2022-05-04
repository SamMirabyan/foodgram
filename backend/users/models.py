from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

    @staticmethod
    def get_default_user():
        deleted, _ = User.objects.get_or_create(username='deleted')
        return deleted.pk
