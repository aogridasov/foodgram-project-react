# Generated by Django 2.2.19 on 2022-12-08 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20221208_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Фото рецепта'),
        ),
    ]
