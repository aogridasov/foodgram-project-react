from django.contrib.auth import get_user_model
from django.db import models

from foodgram.recipes.models import Recipe


User = get_user_model()


class ShoppingCart(models.Model):
    """Модель тега для рецептов"""
    user = models.ForeignKey(
        User,
        related_name='shoppingcart',
        verbose_name='Пользователь'
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты в списке'
    )

    def __str__(self):
        return 'Список покупок ' + self.user
