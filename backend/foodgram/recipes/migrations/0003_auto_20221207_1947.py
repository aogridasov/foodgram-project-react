# Generated by Django 2.2.19 on 2022-12-07 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20221207_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to='', verbose_name='Фото рецепта'),
        ),
    ]