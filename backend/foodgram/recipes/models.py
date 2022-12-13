from colorfield.fields import ColorField
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тега для рецептов"""
    name = models.CharField(max_length=100, verbose_name='Название тега')
    color = ColorField(default='#FF0000',)
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name


class Measure(models.Model):
    """Модель единиц измерения ингредиентов"""
    measurement_unit = models.CharField(max_length=10, verbose_name='Единица измерения')

    def __str__(self):
        return self.measurement_unit


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField(max_length=100, verbose_name='Название ингредиента')
    measurement_unit = models.ForeignKey(
        Measure,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Автор рецепта',
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    name = models.CharField(max_length=256, verbose_name='Название рецепта')
    image = models.ImageField(
        verbose_name='Фото рецепта',
        blank=True,
        null=True,
        upload_to='recipes/'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    cooking_time = models.IntegerField(verbose_name='Время приготовления')

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель для формирования списка избранных рецептов"""
    user = models.ForeignKey(
        User,
        related_name='favorite',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='in_favorite',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f' {self.user.get_username()} сохранил {self.recipe.name}'


class IngredientToRecipe(models.Model):
    """Модель связи ингредиентов с рецептом"""
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Ингредиент',
        related_name='recipe'
    )
    amount = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return 'Ингредиенты рецепта ' + self.recipe.name

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='one_add_per_ingredient'
            )
        ]


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
