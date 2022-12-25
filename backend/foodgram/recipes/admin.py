from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientToRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


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
        'get_ingredients',
        'get_in_favorite_count',
    )
    inlines = [IngredientToRecipeInline, TagRecipeInline, ]
    filter_horizontal = ('tags',)
    search_fields = ('name',)
    list_filter = (
        'pub_date', 'tags', 'cooking_time', 'author', 'name',
    )
    empty_value_display = '-пусто-'

    def get_ingredients(self, obj):
        qs = obj.ingredients.all()
        return [link.ingredient.name for link in qs]

    get_ingredients.short_description = 'Ингредиенты'

    def get_in_favorite_count(self, obj):
        return obj.favorite.count()

    get_in_favorite_count.short_description = 'В избранном'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_editable = ('name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('name',)
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


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite)
admin.site.register(IngredientToRecipe)
admin.site.register(ShoppingCart)
