import base64
import webcolors
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers, exceptions

from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            Favourite,
                            ShoppingCart)
from users.models import Subscription
from foodgram_backend.settings import RECIPE_LIMIT

User = get_user_model()


class Hex2NameColor(serializers.Field):
    """
    Custom serializer field for converting hex color codes to color names.
    """
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for model Tag.
    """
    color = Hex2NameColor

    class Meta:
        model = Tag
        fields = 'id', 'name', 'color', 'slug'


class IngredientSerializer(serializers.ModelSerializer):
    """
        Serializer for model Ingredient.
    """
    class Meta:
        model = Ingredient
        fields = 'id', 'name', 'measurement_unit'


class Base64ImageField(serializers.ImageField):
    """
        Custom serializer field for handling base64 encoded images.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for model RecipeIngredient.
    """
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)

    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = 'id', 'name', 'measurement_unit', 'amount'


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True)

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        return (current_user.is_authenticated
                and Subscription.objects.filter(
                    subscriber=current_user,
                    subscribing=obj).exists())


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Serializer for get-requests to the Recipe model.
    """
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True)
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited',
        read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart',
        read_only=True)
    image = Base64ImageField

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'tags', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        return (current_user.is_authenticated
                and obj.favorite.filter(user=current_user).exists())

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        return (current_user.is_authenticated
                and obj.shopping.filter(user=current_user).exists())


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for creation, modification and deletion of Recipe model object.
    """
    author = CustomUserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        slug_field='id',
        many=True,
        queryset=Tag.objects.all())
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'tags', 'ingredients',
                  'image', 'text', 'cooking_time')

    def _introduce_ingredients_in_recepies(
            self, data_ingredient_amount, recipe):
        ingredients_data = []
        for ingredient_amount in data_ingredient_amount:
            ingredient = Ingredient.objects.get(
                pk=ingredient_amount['ingredient']['id'])
            obj, created = RecipeIngredient.objects.update_or_create(
                ingredient=ingredient,
                recipe=recipe,
                defaults={'amount': ingredient_amount["amount"]})
            ingredients_data.append(obj.ingredient.id)
        return ingredients_data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        data_ingredient_amount = validated_data.pop('recipeingredient_set')
        recipe = super().create(validated_data)
        self._introduce_ingredients_in_recepies(
            data_ingredient_amount, recipe)
        return recipe

    def update(self, instance, validated_data):
        required_fields = ['name', 'image', 'text', 'recipeingredient_set',
                           'tags', 'cooking_time']
        for field in required_fields:
            if field not in validated_data:
                raise serializers.ValidationError(
                    {field: ['Это поле обязательно для изменения.']})
        data_ingredient_amount = validated_data.pop('recipeingredient_set')
        instance = super().update(instance, validated_data)
        ingredients_data = self._introduce_ingredients_in_recepies(
            data_ingredient_amount, instance)
        instance.ingredients.set(ingredients_data)
        instance.save()
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Serializer for outputting a shortened version of Recipe model objects.
    """

    def check_existence(self):
        endpoint = self.context['endpoint']
        method = self.context['method']
        user = self.context['user']
        msg = self.context['msg']
        instance = self.instance

        exists_check = {
            'shopping_cart': {
                'POST': ShoppingCart.objects.filter(
                    user=user, recipe=instance).exists(),
                'DELETE': not ShoppingCart.objects.filter(
                    user=user, recipe=instance).exists()
            },
            'favorite_list': {
                'POST': Favourite.objects.filter(
                    user=user, recipe=instance).exists(),
                'DELETE': not Favourite.objects.filter(
                    user=user, recipe=instance).exists()
            }
        }

        if exists_check.get(endpoint).get(method):
            raise exceptions.ValidationError(f'{msg}')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(CustomUserSerializer):
    """
    Serializer for getting user subscription list.
    """
    recipes = serializers.SerializerMethodField('get_recipes', read_only=True)
    recipes_count = serializers.SerializerMethodField('get_recipes_count',
                                                      read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        subscription_recipes = obj.recipes.all()
        return subscription_recipes.count()

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit', RECIPE_LIMIT)
        recipes = Recipe.objects.filter(author=obj)[:int(limit)]
        return RecipeShortSerializer(instance=recipes, many=True).data

    def check_existence(self):
        method = self.context['method']
        subscriber = self.context['user']
        msg = self.context['msg']
        subscribing = self.instance

        exists_check = {
            'DELETE': not Subscription.objects.filter(
                subscriber=subscriber,
                subscribing=subscribing).exists()
        }

        if exists_check.get(method):
            raise exceptions.ValidationError(f'{msg}')


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password',
                  'id')

    def validate(self, attrs):
        required_attrs = ['first_name', 'last_name']
        current_email = attrs.get('email')
        if User.objects.filter(email=current_email).exists():
            raise serializers.ValidationError(
                {'email': ["Уже есть пользователь с таким email."]})
        for required_attr in required_attrs:
            if attrs.get(required_attr) is None:
                raise serializers.ValidationError(
                    {required_attr: ["Это поле обязательно для заполнения."]})
            if attrs.get(required_attr) == '':
                raise serializers.ValidationError(
                    {required_attr: ["Это поле не должно быть пустым."]})
        return super().validate(attrs)
