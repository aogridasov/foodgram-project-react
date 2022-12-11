from rest_framework import viewsets

from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Measure,
                            Recipe, Tag)
from shopping_cart.models import ShoppingCart
from users.models import Subscribe, User

from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadOnlySerializer, RecipeCUDSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadOnlySerializer
        elif self.action in ('create', 'update', 'destroy'):
            return RecipeCUDSerializer

    def perform_create(self, serializer):
        tags = self.request.data.tags
        ingredients = self.request.data.ingredients
        author = self.request.user
        serializer.save(
            author=author,
            ingredients=ingredients,
            tags=tags,
        )


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
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
