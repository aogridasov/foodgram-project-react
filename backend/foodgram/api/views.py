from rest_framework import viewsets, status, filters
from .mixins import CreateDestroyViewSet

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView

from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Measure,
                            Recipe, Tag)
from shopping_cart.models import ShoppingCart
from users.models import Subscribe, User

from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadOnlySerializer, RecipeCUDSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer, UserSerializer, IngredietToRecipeSerializer,
                          RecipeMiniSerializer, UserIncludeSerializer)

from django.shortcuts import get_object_or_404
from django.http import FileResponse

from shopping_cart import pdf_generator


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadOnlySerializer
        elif self.action in ('create', 'partial_update', 'destroy'):
            return RecipeCUDSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

"""     def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {'is_favorited': self.request.query_params.get('is_favorited', False)},
        )    
        context.update(
            {'is_in_shopping_cart': self.request.query_params.get('is_in_shopping_cart', False)},
        )    
            {'author': self.request.query_params.get('author', False)},
            {'tags': self.request.query_params.get('tags', False)},
        )
        return context """


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


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
        response = UserIncludeSerializer(author, context={'request': request})
        return Response(response.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"recipes_limit": self.request.query_params.get('recipes_limit', False)}
        )
        return context

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
    serializer_class = UserIncludeSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return User.objects.filter(follower__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"recipes_limit": self.request.query_params.get('recipes_limit', False)}
        )
        return context


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
            error = {"errors": "it was already in favorite"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = RecipeMiniSerializer(recipe, context={'request': request})
        return Response(response.data, status=status.HTTP_201_CREATED, headers=headers)

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
        error = {"errors": "it was not in favorite"}
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
            error = {"errors": "it was already in shopping cart"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = RecipeMiniSerializer(recipe, context={'request': request})
        return Response(response.data, status=status.HTTP_201_CREATED, headers=headers)

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
        error = {"errors": "it was not in your shopping cart"}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartDownloadRetrieveAPIView(RetrieveAPIView):
    serializer_class = ShoppingCartSerializer

    def get_ingredients(self):
        recipes = Recipe.objects.filter(shoppingcart__user=self.request.user)
        ingredients_to_recipes = IngredientToRecipe.objects.filter(recipe__in=recipes)

        ingredients = {}

        for link in ingredients_to_recipes:
            ingredient = link.ingredient
            if ingredient in ingredients:
                ingredients[ingredient] += link.amount
            else:
                ingredients[ingredient] = link.amount

        return ingredients

    def get(self, request):
        ingredients = self.get_ingredients()
        pdf = pdf_generator.generate(ingredients)
        return FileResponse(pdf, as_attachment=True, filename='test.pdf')


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
