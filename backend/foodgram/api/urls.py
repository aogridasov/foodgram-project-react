from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')
router.register(
    r'users',
    views.UserViewSet,
    basename='users'
)

urlpatterns = [
    path(
        r'users/me/',
        views.UserSelfViewSet.as_view(),
        name='users-me'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        r'recipes/download_shopping_cart/',
        views.ShoppingCartDownloadRetrieveAPIView.as_view(),
        name='download_shopping_card'
    ),
    path('', include(router.urls)),
]
