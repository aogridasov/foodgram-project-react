import django_filters

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.NumberFilter(
        field_name='author__id', lookup_expr='iexact'
    )
    tags = django_filters.CharFilter(
        field_name='tags__slug', lookup_expr='iexact'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)
