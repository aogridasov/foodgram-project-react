from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.filters import RecipeFilter, IngredientSearchFilter
from api.mixins import CreateDestroyViewSet
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCUDSerializer, RecipeMiniSerializer,
                             RecipeReadOnlySerializer, ShoppingCartSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserIncludeSerializer, UserSerializer)
from recipes import pdf_generator
from recipes.models import (Ingredient, IngredientToRecipe, Recipe,
                            ShoppingCart, Tag, Favorite)
from users.models import User
from rest_framework import permissions
from django.db.models import Exists, OuterRef


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {"recipes_limit": self.request.query_params.get('recipes_limit', False)}
        )
        return context

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        author = get_object_or_404(self.queryset, pk=pk)
        subscription = author.subscribed.filter(user=self.request.user)

        if request.stream.method == 'POST':
            if subscription.exists():
                error = {"error": "already subscribed"}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(
                user=self.request.user,
                author=author
            )
            headers = self.get_success_headers(serializer.data)
            response = UserIncludeSerializer(
                author, context={'request': request}
            )
            return Response(
                response.data, status=status.HTTP_201_CREATED, headers=headers
            )

        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        error = {"error": "you are not subscribed"}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def subscriptions(self, request):
        subscribtions = self.queryset.filter(
            subscribed__user=self.request.user
        )
        page = self.paginate_queryset(subscribtions)

        if page is not None:
            serializer = UserIncludeSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserIncludeSerializer(
            subscribtions, many=True, context={'request': request}
        )
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user_favorited = Favorite.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user,
        )
        user_shoppingcart = ShoppingCart.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user,
        )

        queryset = Recipe.objects.annotate(
            is_favorited=Exists(user_favorited)
        ).annotate(
            is_in_shopping_cart=Exists(user_shoppingcart)
        )
        x = queryset[0]
        x2 = queryset[1]
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadOnlySerializer
        return RecipeCUDSerializer

    @staticmethod
    def create_recipe_link(recipe, link, request, serializer):
        if link.exists():
            error = {"error": "already in"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            user=request.user,
            recipe=recipe,
        )
        response = RecipeMiniSerializer(
            recipe, context={'request': request}
        )
        return Response(
            response.data, status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def delete_recipe_link(link):
        if link.exists():
            link.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        error = {"error": "recipe is not added"}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        serializer = FavoriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(self.queryset, pk=pk)
        in_favorite = recipe.favorite.filter(user=self.request.user)

        return self.create_recipe_link(recipe, in_favorite, request, serializer)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        serializer = FavoriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(self.queryset, pk=pk)
        in_favorite = recipe.favorite.filter(user=self.request.user)

        return self.delete_recipe_link(in_favorite)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        serializer = ShoppingCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(self.queryset, pk=pk)
        in_shoppingcart = recipe.shoppingcart.filter(user=self.request.user)

        return self.create_recipe_link(recipe, in_shoppingcart, request, serializer)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        serializer = ShoppingCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = get_object_or_404(self.queryset, pk=pk)
        in_shoppingcart = recipe.shoppingcart.filter(user=self.request.user)

        return self.delete_recipe_link(in_shoppingcart)


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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
