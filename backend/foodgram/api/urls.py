from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')
router.register(
    r'recipes/(?P<id>\d+)/favorite',
    views.FavoriteViewSet,
    basename='favorite'
)
router.register(
    r'users/(?P<id>\d+)/subscribe',
    views.SubscribeViewSet,
    basename='subscribe'
)
router.register(
    r'recipes/(?P<id>\d+)/shopping_cart',
    views.ShoppingCartViewSet,
    basename='shopping_cart'
)
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path(r'users/subscriptions/', views.SubscibtionsListAPIView.as_view(), name='subscriptions'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
