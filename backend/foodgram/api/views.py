from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCUDSerializer, RecipeMiniSerializer,
                             RecipeReadOnlySerializer, ShoppingCartSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserIncludeSerializer, UserSerializer)
from recipes import pdf_generator
from recipes.models import (Favorite, Ingredient, IngredientToRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(self.queryset, pk=pk)
        serializer = SubscribeSerializer(
            context={
                'request': request,
                'author': author
            },
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
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

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(self.queryset, pk=pk)
        get_object_or_404(
            Subscribe, author=author, user=self.request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        subscribtions = self.queryset.filter(
            subscribed__user=self.request.user
        )
        page = self.paginate_queryset(subscribtions)

        if not page:
            serializer = UserIncludeSerializer(
                subscribtions, many=True, context={'request': request}
            )
            return Response(serializer.data)

        serializer = UserIncludeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Recipe.objects.all()

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
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadOnlySerializer
        return RecipeCUDSerializer

    @staticmethod
    def create_recipe_link(pk, request, link_serializer):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        user = get_object_or_404(User, pk=data['user'])
        recipe = get_object_or_404(Recipe, pk=data['recipe'])
        serializer = link_serializer(
            data=data, context={'request': request}
        )   
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=user,
            recipe=recipe
        )
        response = RecipeMiniSerializer(
            Recipe.objects.get(id=pk), context={'request': request}
        )
        return Response(
            response.data, status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def delete_recipe_link(pk, request, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        get_object_or_404(model, recipe=recipe, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        return self.create_recipe_link(pk, request, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        return self.delete_recipe_link(pk, request, Favorite)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        return self.create_recipe_link(pk, request, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        return self.delete_recipe_link(pk, request, ShoppingCart)

    @action(detail=False)
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(shoppingcart__user=self.request.user)
        ingredients_to_recipes = IngredientToRecipe.objects.filter(
            recipe__in=recipes
        )
        pdf = pdf_generator.generate(ingredients_to_recipes)
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
