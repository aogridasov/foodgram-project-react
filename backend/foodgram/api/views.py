from rest_framework import viewsets

from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Measure,
                            Recipe, Tag)
from shopping_cart.models import ShoppingCart
from users.models import Subscribe, User

from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadOnlySerializer, RecipeCUDSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer, UserSerializer, IngredietToRecipeSerializer)

from django.shortcuts import get_object_or_404


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadOnlySerializer
        elif self.action in ('create', 'partial_update', 'destroy'):
            return RecipeCUDSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('id'))

    def get_queryset(self):
        return self.get_recipe().in_favorite.all()

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=self.get_recipe()
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
