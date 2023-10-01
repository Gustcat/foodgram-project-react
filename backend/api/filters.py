from django_filters import rest_framework as filters

from recipes.models import Recipe, Ingredient, Tag


class RecipeFilter(filters.FilterSet):
    """
    Class for filtering recipes by field: author, tags, is_favorited,
    is_in_shopping_cart.
    """
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags']


class IngredientFilter(filters.FilterSet):
    """
    Class for searching ingredients by name.
    """
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
