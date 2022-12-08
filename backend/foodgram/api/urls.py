from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
#router.register('subsc', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')
#router.register('recipes', views.RecipeViewSet, basename='recipes')


urlpatterns = [
    path('/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt'))
]
