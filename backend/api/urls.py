from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views as api_views

router = DefaultRouter()
router.register('tags', api_views.TagViewSet)
router.register('ingredients', api_views.IngredientViewSet)
router.register('recipes', api_views.RecipeReadOnlyViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
