from rest_framework import viewsets, filters
from django.contrib.auth import get_user_model
from recipes.models import (Ingredient,
                            Tag,
                            Recipe)
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeReadSerializer,
                          RecipeWriteSerializer,
                          SubscribeSerializer)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        user = User.objects.get(username=self.request.user)
        subscribed_users = User.objects.filter(subscribing__subscriber=user)
        return subscribed_users

    # def perform_create(self, serializer):
    #     user = get_object_or_404(User, id=self.kwargs.get('user_id'))
    #     serializer.save(subscriber=self.request.user, subscribing=user)
    #
    # def perform_update(self, serializer):
    #     user = get_object_or_404(User, id=self.kwargs.get('user_id'))
    #     serializer.save(subscriber=self.request.user, subscribing=user)

