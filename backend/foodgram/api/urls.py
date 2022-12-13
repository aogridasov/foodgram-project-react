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
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
