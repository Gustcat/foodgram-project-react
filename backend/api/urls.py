from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter, Route

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionViewSet,
    SubscribeViewSet)

app_name = 'api'


class CustomRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}$',
            mapping={'post': 'create', 'delete': 'destroy'},
            name='{basename}-custom',
            initkwargs={'suffix': '-custom'},
            detail=False,
        ),
    ]


customrouter = CustomRouter()
customrouter.register(r'users/(?P<user_id>\d+)/subscribe/',
                      SubscribeViewSet,
                      basename='subscribe')

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'users/subscriptions',
                SubscriptionViewSet,
                basename='subscribtions')

urlpatterns = [
    path('', include(customrouter.urls)),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
