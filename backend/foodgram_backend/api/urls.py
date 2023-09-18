from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter, Route
from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionViewSet,
    SubscribeViewSet,
    FavoriteViewSet,
    ShoppingCartViewSet,
    DownloadViewSet)

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
customrouter.register(r'recipes/(?P<recipe_id>\d+)/favorite/',
                      FavoriteViewSet,
                      basename='favorite')
customrouter.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart/',
                      ShoppingCartViewSet,
                      basename='shopping_cart')

router = DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes/download_shopping_cart',
                DownloadViewSet,
                basename='shopping_cart_download')
router.register(r'recipes', RecipeViewSet)
router.register(r'users/subscriptions',
                SubscriptionViewSet,
                basename='subscribtions')

urlpatterns = [
    path('', include(customrouter.urls)),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
