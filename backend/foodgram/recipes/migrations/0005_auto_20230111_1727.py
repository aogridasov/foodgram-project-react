# Generated by Django 3.2 on 2023-01-11 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230111_1722'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'default_related_name': 'favorite', 'verbose_name': 'В избранном', 'verbose_name_plural': 'В избранном'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': 'shoppingcart', 'verbose_name': 'В списке покупок', 'verbose_name_plural': 'В списке покупок'},
        ),
    ]
