import csv
from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Import tags from csv file'

    def handle(self, *args, **kwargs):
        with open('/app/data/tags.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, color, slug = row
                if Tag.objects.filter(
                        name=name,
                        color=color,
                        slug=slug).exists():
                    continue
                Tag.objects.create(
                    name=name, color=color, slug=slug)
