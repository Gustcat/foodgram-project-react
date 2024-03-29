from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram_backend.settings import STANDARTLENGTH

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=STANDARTLENGTH,
        unique=True,
        blank=False,
        verbose_name='Название тега')
    color = models.CharField(
        max_length=7,
        unique=True,
        blank=False,
        verbose_name='Цвет')
    slug = models.SlugField(
        max_length=STANDARTLENGTH,
        unique=True,
        blank=False,
        verbose_name='Слаг')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=STANDARTLENGTH,
        verbose_name='Название ингредиента',
        blank=False,
        db_index=True)
    measurement_unit = models.CharField(
        max_length=STANDARTLENGTH,
        verbose_name='Единицы измерения',
        blank=False)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='Автор')
    name = models.CharField(
        max_length=STANDARTLENGTH,
        verbose_name='Название рецепта',
        blank=False,)
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False)
    text = models.TextField(
        blank=False,
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        blank=False,)
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        blank=False,
        verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(1000)],
        blank=False,
        verbose_name='Время приготовления',
        help_text='в минутах')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Дата создания')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['name', 'author'],
            name='unique_name_author')]

    def __str__(self):
        return f'{self.name} {self.author}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(1000)],
        verbose_name='Количество')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient')]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'tag'],
            name='unique_recipe_tag')]

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт продуктовой корзины',
        related_name='shopping')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_favorite_recipe')]

    def __str__(self):
        return f'{self.recipe} {self.user}'


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='favorite')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_recipe_in_shopping_cart')]

    def __str__(self):
        return f'{self.recipe} {self.user}'
