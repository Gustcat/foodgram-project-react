from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200,
                            unique=True,
                            blank=False,
                            verbose_name='Название тега')
    color = models.CharField(max_length=10,
                             unique=True,
                             blank=False,
                             verbose_name='Цвет')
    slug = models.SlugField(max_length=200,
                            unique=True,
                            blank=False,
                            verbose_name='Слаг')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название ингредиента',
                            blank=False)
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единицы измерения',
                                        blank=False)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name='recipes',
                               on_delete=models.CASCADE,
                               blank=False,
                               verbose_name='Автор')
    name = models.CharField(max_length=200,
                            verbose_name='Название рецепта',
                            blank=False,)
    image = models.ImageField(upload_to='recipes/images/',
                              blank=False,)
    text = models.TextField(blank=False,
                            verbose_name='Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient',
                                         blank=False,)
    tags = models.ManyToManyField(Tag,
                                  through='RecipeTag',
                                  blank=False,
                                  verbose_name='Теги')
    cooking_time = models.IntegerField(validators=[MinValueValidator(1),
                                                   MaxValueValidator(1000)],
                                       blank=False,
                                       verbose_name='Время приготовления',
                                       help_text='в минутах')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    editable=False,
                                    verbose_name='Дата создания')

    def __str__(self):
        return f'{self.name} {self.author}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    amount = models.IntegerField(validators=[MinValueValidator(1),
                                             MaxValueValidator(1000)],
                                 verbose_name='Количество')

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            verbose_name='Тег')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    def __str__(self):
        return f'{self.recipe} {self.tag}'
