from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer

from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Measure,
                            Recipe, Tag)
from shopping_cart.models import ShoppingCart
from users.models import Subscribe, User


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        return obj.follower.filter(id__exact=current_user.id).exists()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredietToRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient')
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientToRecipe
        fields = ('name', 'measurement_unit', 'amount')

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit.measurement_unit


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения одного / списка рецептов"""
    tags = TagSerializer(many=True)
    ingredients = IngredietToRecipeSerializer(many=True)
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'pub_date',
            'name',
            'text',
            'tags',
            'cooking_time',
            'ingredients'
        )
        read_only_fields = fields


class RecipeCUDSerializer(serializers.ModelSerializer):
    """Сериалайзер для CREATE/PATCH/DELETE запросов к рецептам"""
    ingredients = ????
    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'pub_date',
            'name',
            'text',
            'tags',
            'cooking_time',
            'ingredients'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
