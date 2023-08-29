from django.contrib.auth import get_user_model
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            RecipeTag)

from rest_framework.serializers import (
    ModelSerializer,
    SlugRelatedField,
    ValidationError,
)


User = get_user_model()


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = 'id', 'name', 'color', 'slug'


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = 'id', 'name', 'measurement_unit'
