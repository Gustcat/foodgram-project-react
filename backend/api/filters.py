import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Class for filtering recipes by field: author, tags, is_favorited,
    is_in_shopping_cart.
    """
    is_favorited = django_filters.CharFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart')
    tags = django_filters.CharFilter(method='filter_tags')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value == '1':
            queryset = queryset.filter(favorite__user=user.id)
        elif value == '0':
            queryset = queryset.exclude(favorite__user=user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value == '1':
            queryset = queryset.filter(shopping__user=user.id)
        elif value == '0':
            queryset = queryset.exclude(shopping__user=user.id)
        return queryset

    def filter_tags(self, queryset, name, value):
        return queryset.filter(tags__slug=value)

    class Meta:
        model = Recipe
        fields = ['author']
