from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientToRecipe, Measure, Recipe,
                     Tag)

admin.site.register(IngredientToRecipe)


class IngredientToRecipeInline(admin.StackedInline):
    model = IngredientToRecipe
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'pub_date',
        'name',
        'image',
        'text',
        'cooking_time',
    )
    inlines = [IngredientToRecipeInline, ]
    filter_horizontal = ('tags',)
    list_editable = ('name', 'image', 'text', 'cooking_time',)
    search_fields = ('name', 'text', 'tags', 'cooking_time',)
    list_filter = ('pub_date', 'tags', 'cooking_time')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
    )
    list_editable = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class MeasureAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'measurement_unit',
    )
    list_editable = ('measurement_unit',)
    search_fields = ('measurement_unit',)
    list_filter = ('measurement_unit',)
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
admin.site.register(Measure, MeasureAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
