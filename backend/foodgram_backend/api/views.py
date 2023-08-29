from rest_framework import viewsets, filters
from django.contrib.auth import get_user_model
from recipes.models import (Ingredient,
                            Tag)
from .serializers import (TagSerializer,
                          IngredientSerializer,)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)
