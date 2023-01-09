from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')
router.register(
    'users',
    views.UserViewSet,
    basename='users'
)

urlpatterns = [
    path(
        r'users/subscriptions/',
        views.UserViewSet.as_view({'get': 'subscriptions'}),
        name='subscriptions'
    ),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
