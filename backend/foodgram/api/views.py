from rest_framework import viewsets
from .mixins import CreateDestroyViewSet

from rest_framework.response import Response
from rest_framework import status

from rest_framework.decorators import action
from rest_framework.generics import ListAPIView

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


class SubscribeViewSet(CreateDestroyViewSet):
    serializer_class = SubscribeSerializer

    def get_author(self):
        return get_object_or_404(User, pk=self.kwargs.get('id'))

    def get_queryset(self):
        return self.get_author().follower.all()

    def create(self, request, id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        author = self.get_author()
        if author.follower.filter(user=self.request.user).exists():
            error = {"error": "already subscribed"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = {"msg": "success!"}
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            author=self.get_author()
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, id):
        author = self.get_author()
        follow = author.follower.filter(user=request.user)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        error = {"error": "you are not subscribed"}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class SubscibtionsListAPIView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(follower__user=self.request.user)


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('id'))

    def get_queryset(self):
        return self.get_recipe().in_favorite.all()

    def create(self, request, id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipe = self.get_recipe()
        if recipe.in_favorite.filter(user=self.request.user).exists():
            error = {"error": "it was already in favorite"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = {"msg": "success!"}
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=self.get_recipe()
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, id):
        recipe = self.get_recipe()
        bookmark = recipe.in_favorite.filter(user=request.user)
        if bookmark.exists():
            bookmark.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        error = {"error": "it was not in favorite"}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('id'))

    def get_queryset(self):
        return self.get_recipe().shoppingcart.all()

    def create(self, request, id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipe = self.get_recipe()
        if recipe.shoppingcart.filter(user=self.request.user).exists():
            error = {"error": "it was already in shopping cart"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = {"msg": "success!"}
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=self.get_recipe()
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, id):
        recipe = self.get_recipe()
        shoppingcart = recipe.shoppingcart.filter(user=request.user)
        if shoppingcart.exists():
            shoppingcart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        error = {"error": "it was not in your shopping cart"}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class SubscibtionsListAPIView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(follower__user=self.request.user)



class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
