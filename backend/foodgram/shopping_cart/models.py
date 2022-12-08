from django.db import models

from recipes.models import Recipe
from users.models import User


class ShoppingCart(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(
        User,
        related_name='shoppingcart',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты в списке'
    )

    def __str__(self):
        return 'Список покупок ' + self.user
