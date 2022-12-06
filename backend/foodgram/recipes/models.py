from django.db import models
from django.contrib.auth import get_user_model

from colorfield.fields import ColorField


User = get_user_model()


class Tag(models.Model):
    """Модель тега для рецептов"""
    title = models.CharField(max_length=100, verbose_name='Название тега')
    hex_code = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    

class Measure(models.Model):
    """Модель единиц измерения ингредиентов"""
    units = models.CharField(max_length=10)    # choicefield?


class Ingredient(models.Model):
    """Модель ингредиента"""
    title = models.CharField(max_length=100, verbose_name='Название ингредиента')
    quantity = models.IntegerField()
    measure = models.ManyToManyField(Measure)


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User, 
        null=True,
        on_delete=models.SET_NULL, 
        verbose_name='Автор рецепта', 
    )
    title = models.CharField(max_length=256, verbose_name='Название рецепта')
    image = models.ImageField(verbose_name='Фото рецепта')
    description = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(Ingredient, verbose_name='Список иннгредиентов')
    tag = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.IntegerField(verbose_name='Время приготовления') # Нужна валидация на минуты? или конвертация в часы?
    
    def __str__(self):
        return 'Рецепт: ' + self.title

class Bookmark(models.Model):
    """Модель для формирования списка избранных рецептов"""
    user = models.ForeignKey(
        User, 
        null=True,
        on_delete=models.CASCADE, 
        verbose_name='Пользователь', 
    )
    recipes = models.ManyToManyField(Recipe)


class IngredientToRecipe(models.Model):
    """Модель связи ингредиентов с рецептом"""
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    ingredient = ?? # прописать в модели ингредиента?
    amount = models.IntegerField()

class ShoppingCart(models.Model):
    """Модель списка покупок"""
    
    