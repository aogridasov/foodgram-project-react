from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тега для рецептов"""
    name = models.CharField(
        max_length=settings.RECIPES_MODELS_NAMES_LENGTH,
        unique=True,
        verbose_name='Название тега',
    )
    color = ColorField(default='#FF0000', unique=True, verbose_name='Цвет')
    slug = models.SlugField(
        max_length=settings.RECIPES_MODELS_NAMES_LENGTH,
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField(
        max_length=settings.RECIPES_MODELS_NAMES_LENGTH,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=settings.RECIPES_MODELS_NAMES_LENGTH,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Автор рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации',
    )
    name = models.CharField(
        max_length=settings.RECIPES_MODELS_NAMES_LENGTH,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        blank=True,
        null=True,
        upload_to='recipes/images/',
        verbose_name='Фото рецепта',
    )
    text = models.TextField(verbose_name='Описание рецепта')
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Время приготовления',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


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
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1), ]
    )

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'

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
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Связь тега и рецепта'

        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='one_add_per_tag'
            )
        ]


class UserRecipeLink(models.Model):
    """Абстрактная модель для связи юзера и рецепта через ForeignKey"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_unique_user_recipe_link'
            )
        ]

    def __str__(self):
        return f' {self.user.get_username()} добавил {self.recipe.name} в {self.__class__.__name__}'


class Favorite(UserRecipeLink):
    """Модель для формирования списка избранных рецептов"""
    class Meta(UserRecipeLink.Meta):
        verbose_name = 'В избранном'
        verbose_name_plural = 'В избранном'
        default_related_name = 'favorite'


class ShoppingCart(UserRecipeLink):
    """Модель для формирования списка покупок"""
    class Meta(UserRecipeLink.Meta):
        verbose_name = 'В списке покупок'
        verbose_name_plural = 'В списке покупок'
        default_related_name = 'shoppingcart'
