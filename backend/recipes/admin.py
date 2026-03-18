from django.contrib import admin
from .models import (
    Tag, Ingredient, Recipe, IngredientInRecipe,
    Favorite, ShoppingCart
)


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_favorite_count')
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username', 'author__email')
    inlines = (IngredientInline,)

    def get_favorite_count(self, obj):
        return obj.favorited_by.count()

    get_favorite_count.short_description = 'Добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')