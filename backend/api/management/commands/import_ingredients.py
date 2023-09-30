import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from csv file'

    def handle(self, *args, **kwargs):
        with open('/app/data/ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, measurement_unit = row
                if Ingredient.objects.filter(
                        name=name,
                        measurement_unit=measurement_unit).exists():
                    continue
                Ingredient.objects.create(
                    name=name, measurement_unit=measurement_unit)
