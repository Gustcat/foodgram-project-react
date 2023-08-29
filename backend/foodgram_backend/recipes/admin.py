from django.contrib import admin
from django.contrib.auth.models import User
from .models import (Recipe,
                     Ingredient,
                     Tag,
                     RecipeIngredient,
                     RecipeTag)


User._meta.get_field('username').verbose_name = 'Имя автора'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'name',
                    'author_name',
                    'display_tags',
                    'display_ingredients',
                    'cooking_time'
                    )
    search_fields = ('author__username', 'name',)
    list_filter = ('author__username', 'name', 'tags', 'pub_date')
    list_editable = ('name',)

    #filter_horizontal = ('tags',)

    def author_name(self, obj):
        return obj.author.username

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def display_ingredients(self, obj):
        return ", ".join([ingredient.name for ingredient in obj.ingredients.all()])

    author_name.short_description = 'Автор'
    display_tags.short_description = 'Теги'
    display_ingredients.short_description = 'Ингредиенты'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('name', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe_name', 'ingredient_name', 'amount')
    search_fields = ('recipe__name', 'ingredient__name',)
    list_filter = ('recipe__name', 'ingredient__name',)

    def recipe_name(self, obj):
        return obj.recipe.name

    def ingredient_name(self, obj):
        return obj.ingredient.name

    recipe_name.short_description = 'Автор'
    ingredient_name.short_description = 'Теги'


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe_name', 'tag_name',)
    search_fields = ('recipe__name', 'tag__name',)
    list_filter = ('recipe__name', 'tag__name',)

    def recipe_name(self, obj):
        return obj.recipe.name

    def tag_name(self, obj):
        return obj.tag.name

    recipe_name.short_description = 'Автор'
    tag_name.short_description = 'Теги'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
