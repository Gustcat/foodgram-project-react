from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    SubscribeViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'users/subscribtions', SubscribeViewSet, basename='subscribtions')
# router.register(r'users/(?P<user_id>\d+)/subscribe', SubscribeViewSet,
#                 basename='subscribe')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
