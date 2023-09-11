import base64
import webcolors
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            RecipeTag,
                            Favourite,
                            ShoppingCart)
from users.models import Subscription
from users.serializers import CustomUserSerializer

User = get_user_model()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor

    class Meta:
        model = Tag
        fields = 'id', 'name', 'color', 'slug'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = 'id', 'name', 'measurement_unit'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = 'id', 'name', 'measurement_unit', 'amount'


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set',
                                             many=True)
    is_favorited = serializers.SerializerMethodField('get_is_favorited',
                                                     read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart', read_only=True)
    image = Base64ImageField

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'tags', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.username == '':
            return False
        return Favourite.objects.filter(user=current_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        if current_user.username == '':
            return False
        return ShoppingCart.objects.filter(user=current_user,
                                           recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(slug_field='id', many=True,
                                        queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set',
                                             many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'tags', 'ingredients',
                  'image', 'text', 'cooking_time')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        data_ingredient_amount = validated_data.pop('recipeingredient_set')
        recipe = super().create(validated_data)
        for ingredient_amount in data_ingredient_amount:
            ingredient = Ingredient.objects.get(pk=ingredient_amount
            ['ingredient']['id'])
            RecipeIngredient.objects.create(ingredient=ingredient,
                                            recipe=recipe,
                                            amount=ingredient_amount["amount"])
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        tags_data = validated_data['tags']
        instance.tags.set(tags_data)

        data_ingredient_amount = validated_data['recipeingredient_set']
        ingredients_data = []
        for ingredient_amount in data_ingredient_amount:
            ingredient = Ingredient.objects.get(pk=ingredient_amount
            ['ingredient']['id'])
            obj, created = RecipeIngredient.objects. \
                update_or_create(ingredient=ingredient,
                                 recipe=instance,
                                 defaults={'amount': ingredient_amount["amount"]})
            ingredients_data.append(obj.ingredient.id)
        instance.ingredients.set(ingredients_data)
        instance.save()
        return instance


class SubscribeSerializer(CustomUserSerializer):
    recipes = RecipeReadSerializer(many=True,
                                   read_only=True)
    recipes_count = serializers.SerializerMethodField('get_recipes_count',
                                                      read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        subscription_recipes = obj.recipes.all()
        return subscription_recipes.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        recipes_data = data['recipes']
        limited_recipes_data = []
        for recipe_data in recipes_data:
            limited_recipe_data = {
                key: recipe_data[key]
                for key in ['id', 'name', 'image', 'cooking_time']
                if key in recipe_data
            }
            limited_recipes_data.append(limited_recipe_data)
        data['recipes'] = limited_recipes_data
        return data
