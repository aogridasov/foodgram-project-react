from django.contrib import admin

from .models import Bookmark, Ingredient, IngredientToRecipe, Measure, Recipe, Tag


admin.site.register(IngredientToRecipe)


class IngredientToRecipeInline(admin.StackedInline):
    model = IngredientToRecipe
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'pub_date',
        'title',
        'image',
        'description',
        'cooking_time',
    )
    inlines = [IngredientToRecipeInline, ]
    filter_horizontal = ('tag',)
    list_editable = ('title', 'image', 'description', 'cooking_time',)
    search_fields = ('title', 'description', 'tag', 'cooking_time',)
    list_filter = ('pub_date', 'tag', 'cooking_time')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
    )
    list_editable = ('title',)
    search_fields = ('title',)
    empty_value_display = '-пусто-'


class MeasureAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'units',
    )
    list_editable = ('units',)
    search_fields = ('units',)
    list_filter = ('units',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'slug',
        'title',
        'hex_code',
    )
    list_editable = ('title', 'hex_code',)
    search_fields = ('title',)
    empty_value_display = '-пусто-'


class BookmarkAdmin(admin.ModelAdmin):
    list_display = (
        'user',
    )
    search_fields = ('user',)
    filter_horizontal = ('recipes',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Measure, MeasureAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
