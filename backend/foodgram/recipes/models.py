from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тега для рецептов"""
    title = models.CharField(max_length=100, verbose_name='Название тега')
    hex_code = ColorField(default='#FF0000',)
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return 'Тэг: ' + self.title


class Measure(models.Model):
    """Модель единиц измерения ингредиентов"""
    units = models.CharField(max_length=10, verbose_name='Единица измерения')    # choicefield?

    def __str__(self):
        return str(self.units)


class Ingredient(models.Model):
    """Модель ингредиента"""
    title = models.CharField(max_length=100, verbose_name='Название ингредиента')

    def __str__(self):
        return 'Ингредиент: ' + self.title


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
    title = models.CharField(max_length=256, verbose_name='Название рецепта')
    image = models.ImageField(verbose_name='Фото рецепта', null=True)
    description = models.TextField(verbose_name='Описание рецепта')
    tag = models.ManyToManyField(Tag, verbose_name='Теги', related_name='recipes')
    cooking_time = models.IntegerField(verbose_name='Время приготовления') # Нужна валидация на минуты? или конвертация в часы?

    def __str__(self):
        return 'Рецепт: ' + self.title


class Bookmark(models.Model):
    """Модель для формирования списка избранных рецептов"""
    user = models.ForeignKey(
        User,
        related_name='bookmarks',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
        related_name='bookmarks',
    )

    def __str__(self):
        return 'Закладки пользователя: ' + self.user.get_username()


class IngredientToRecipe(models.Model):
    """Модель связи ингредиентов и едениц измерения с рецептом"""
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='recipe'
    )
    measure = models.ForeignKey(
        Measure,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Единица измерения'
    )
    amount = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return 'Игредиенты рецепта ' + self.recipe.title

#class ShoppingCart(models.Model):
#    """Модель списка покупок"""
