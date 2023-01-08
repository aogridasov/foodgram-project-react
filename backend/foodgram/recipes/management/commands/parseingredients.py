import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


ING_PATH = str(settings.BASE_DIR) + '/data/ingredients.csv'


class Command(BaseCommand):
    help = 'Загружает CSV с ингредиентами в БД проекта'

    def handle(self, *args, **options):
        with open(ING_PATH, newline='', encoding='UTF-8') as ingredients:
            reader = csv.reader(ingredients)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
