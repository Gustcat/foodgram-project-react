from rest_framework import viewsets, filters
from django.contrib.auth import get_user_model
from recipes.models import (Ingredient,
                            Tag,
                            Recipe)
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeReadSerializer,
                          RecipeWriteSerializer)
from django.shortcuts import get_object_or_404


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

    # def perform_create(self, serializer):
    #     print(self.request.user)
    #     serializer.save(author=self.request.user)

    # def get_queryset(self):
    #     queryset = Recipe.objects.all()
    #     genre_slug = self.request.query_params.get('genre')
    #     category__slug = self.request.query_params.get('category')
    #     if genre_slug is not None:
    #         queryset = queryset.filter(genre__slug=genre_slug)
    #     if category__slug is not None:
    #         queryset = queryset.filter(category__slug=category__slug)
    #     return queryset