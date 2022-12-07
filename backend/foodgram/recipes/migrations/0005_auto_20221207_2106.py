# Generated by Django 2.2.19 on 2022-12-07 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20221207_2003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='measure',
        ),
        migrations.AddField(
            model_name='ingredienttorecipe',
            name='measure',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipes.Measure', verbose_name='Единица измерения'),
        ),
    ]
