from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientToRecipe, Recipe,
                     Tag, ShoppingCart, TagRecipe)


class IngredientToRecipeInline(admin.StackedInline):
    model = IngredientToRecipe
    extra = 0
    min_num = 1


class TagRecipeInline(admin.StackedInline):
    model = TagRecipe
    extra = 0
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'pub_date',
        'name',
    )
    inlines = [IngredientToRecipeInline, TagRecipeInline, ]
    filter_horizontal = ('tags',)
    list_editable = ('name',)
    search_fields = ('name',)
    list_filter = ('pub_date', 'tags', 'cooking_time', 'author',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
    )
    list_editable = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'slug',
        'name',
        'color',
    )
    list_editable = ('name', 'color',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
    )
    search_fields = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(IngredientToRecipe)
admin.site.register(ShoppingCart)
