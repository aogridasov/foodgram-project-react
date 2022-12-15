from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Measure,
                            Recipe, Tag, TagRecipe)
from shopping_cart.models import ShoppingCart
from users.models import Subscribe, User


class CurrentAuthorDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['view'].kwargs['id']

    def __repr__(self):
        return '%s()' % self.__class__.__name__


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
        return obj.follower.filter(user=current_user).exists()


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)

    def get_measurement_unit(self, obj):
        return obj.measurement_unit.measurement_unit


class IngredietToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit.measurement_unit

    def get_name(self, obj):
        return obj.ingredient.name


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    name = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)

    def get_name(self, obj):
        return obj.name

    def get_color(self, obj):
        return obj.color

    def get_slug(self, obj):
        return obj.slug


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериалайзер для чтения одного / списка рецептов"""
    tags = TagSerializer(many=True)
    ingredients = IngredietToRecipeSerializer(many=True)
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

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        return obj.in_favorite.filter(user=current_user).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        return obj.shoppingcart.filter(user=current_user).exists()


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
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes

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
        read_only=False,
        required=False
    )
    tags = TagSerializer(many=True, read_only=False, required=False)

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
        )

    def validate_cooking_time(self, value):
        if not (value >= 1):
            raise serializers.ValidationError(
                'Меньше чем за минуту ничего не приготовить :)'
            )
        return value

    def validate_name(self, value):
        length = len(value)
        if not (0 < length < 200):
            raise serializers.ValidationError(
                'Слишком длинное / короткое название!'
            )
        return value

    def to_internal_value(self, data):
        try:
            tags_id = data['tags']
            tags = []
            for tag_id in tags_id:
                tag = {'id': tag_id}
                tags.append(tag)
            data['tags'] = tags
        except KeyError:
            pass

        try:
            ingredients = []
            for ingredient_data in data['ingredients']:
                ingredient_id = ingredient_data['id']
                amount = ingredient_data['amount']

                ingredient_amount_json = {}
                ingredient_amount_json['id'] = ingredient_id
                ingredient_amount_json['amount'] = amount

                ingredients.append(ingredient_amount_json)
            data['ingredients'] = ingredients
        except KeyError:
            pass

        return super(RecipeCUDSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredient_to_recipe = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            current_tag = Tag.objects.get(**tag)
            TagRecipe.objects.create(tag=current_tag, recipe=recipe)

        for ingredient_data in ingredient_to_recipe:
            amount = ingredient_data.pop('amount')
            current_ingredient = Ingredient.objects.get(**ingredient_data)
            IngredientToRecipe.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredient_to_recipe = validated_data.pop('ingredients')

        for tag in tags:
            current_tag = Tag.objects.get(**tag)
            TagRecipe.objects.get_or_create(tag=current_tag, recipe=instance)

        for ingredient_data in ingredient_to_recipe:
            amount = ingredient_data.pop('amount')
            amount_update = {'amount': amount}
            current_ingredient = Ingredient.objects.get(**ingredient_data)
            IngredientToRecipe.objects.update_or_create(
                ingredient=current_ingredient,
                recipe=instance,
                defaults=amount_update
            )

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe',)
        read_only_fields = fields


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')
        read_only_fields = fields


class SubscribeSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True,
        default=CurrentAuthorDefault(),
    )

    class Meta:
        model = Subscribe
        fields = ('author',)
