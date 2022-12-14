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
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shoppingcart',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.recipe} в списке покупок {self.user}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_addition'
            )
        ]