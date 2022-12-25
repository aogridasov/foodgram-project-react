from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from django.shortcuts import get_object_or_404


class CurrentRecipeDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].parser_context['kwargs']['pk']

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class UserSerializer(DjoserUserSerializer):
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
        request = self.context['request']
        if request:
            if request.user.is_anonymous:
                return False
            return obj.subscribed.filter(user=request.user).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredietToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    name = serializers.SerializerMethodField()

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'name', 'amount')

    def get_name(self, obj):
        return obj.ingredient.name


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения одного / списка рецептов"""
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

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
            'ingredients',
            'image',
            'is_favorited',
            'is_in_shopping_cart',
        )
        read_only_fields = fields

    def get_ingredients(self, obj):
        ingredients = Ingredient.objects.filter(recipe__recipe=obj).distinct()
        return IngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context['request']
        if request:
            if request.user.is_anonymous:
                return False
            return obj.favorite.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request:
            if request.user.is_anonymous:
                return False
            return obj.shoppingcart.filter(user=request.user).exists()
        return False


class RecipeMiniSerializer(RecipeReadOnlySerializer):
    """read-only мини версия отображения рецепта с меньшим кол-вом полей"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserIncludeSerializer(UserSerializer):
    """Дополнительный сериалайзер пользователя
    для использования в других вью / сериалайзерах"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = (
            self._context['request'].query_params.get('recipes_limit', False)
        )
        recipes = obj.recipes
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        serializer = RecipeMiniSerializer(
            recipes,
            many=True,
            context=self.context
        )
        return serializer.data


class RecipeCUDSerializer(serializers.ModelSerializer):
    """Сериалайзер для CREATE/PATCH/DELETE запросов к рецептам"""
    ingredients = IngredietToRecipeSerializer(
        many=True,
        required=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        queryset=Tag.objects.all(),
        required=True,
    )
    image = Base64ImageField(required=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'tags',
            'cooking_time',
            'ingredients',
            'image',
            'author',
        )

    def validate_tags(self, value):
        for tag in value:
            if value.count(tag) > 1:
                raise serializers.ValidationError(
                    'Теги не должны повторяться!'
                )
        return value

    def validate_ingredients(self, value):
        for ingredient in value:
            counter = 0
            for dict in value:
                if dict['id'] == ingredient['id']:
                    counter += 1
                    if counter > 1:
                        raise serializers.ValidationError(
                            'Ингредиенты не должны повторяться!'
                        )
        return value

    def to_representation(self, instance):
        """Дополняет вывод информации о тегах и ингредиентах
        при успешном создании рецепта"""
        data = super().to_representation(instance)

        tags_id = data['tags']
        tags = Tag.objects.filter(pk__in=tags_id)
        tags_serialized = TagSerializer(tags, many=True).data
        data['tags'] = tags_serialized

        for ingr_data in data['ingredients']:
            id = ingr_data['id']
            ingredient_link = get_object_or_404(IngredientToRecipe, pk=id)
            measure = ingredient_link.ingredient.measurement_unit
            ingr_id = ingredient_link.ingredient.pk
            ingr_data['measurement_unit'] = measure
            ingr_data['id'] = ingr_id

        return data

    @staticmethod
    def ingredient_to_recipe_link(recipe, ingredient_to_recipe):

        ingredients_to_recipe_data = []
        for ingredient_data in ingredient_to_recipe:
            amount = ingredient_data.pop('amount')
            current_ingredient = Ingredient.objects.get(**ingredient_data)
            ingredients_to_recipe_data.append(
                IngredientToRecipe(
                    ingredient=current_ingredient,
                    amount=amount,
                    recipe=recipe,
                )
            )

        IngredientToRecipe.objects.bulk_create(ingredients_to_recipe_data)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredient_to_recipe = validated_data.pop('ingredients')
        author = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        self.ingredient_to_recipe_link(recipe, ingredient_to_recipe)
        return recipe

    def update(self, instance, validated_data):
        try:
            tags = validated_data.pop('tags')
            ingredient_to_recipe = validated_data.pop('ingredients')
        except KeyError:
            raise serializers.ValidationError(
                'Не все поля заполнены!'
            )
        instance.tags.set(tags)
        instance.ingredients.all().delete()
        self.ingredient_to_recipe_link(instance, ingredient_to_recipe)
        return super().update(instance, validated_data)


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentRecipeDefault(),
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe',)

        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentRecipeDefault(),
    )

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')
        read_only_fields = fields

        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class SubscribeSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Subscribe
        fields = ('author',)
