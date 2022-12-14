# Generated by Django 2.2.19 on 2022-12-14 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20221214_1703'),
        ('shopping_cart', '0002_shoppingcart_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppingcart',
            name='recipes',
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.Recipe', verbose_name='Рецепт'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_recipe_addition'),
        ),
    ]
