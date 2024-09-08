import csv

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Category, Comment, User, Genre, Review, Title

TABLES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    """
    Imports data from csv files to database via the following command:
    python manage.py load_csv.

    To update the database:
    1) Remove db.sqlite3
    2) Make migrations (python manage.py migrate).

    A new empty database will appear.
    """
    help = "Import data from csv files."

    def handle(self, *args, **kwargs):
        try:
            for model, filename in TABLES.items():
                with open(
                    f'{settings.BASE_DIR}/static/data/{filename}',
                    'r',
                    encoding='utf-8'
                ) as csv_file:
                    reader = csv.DictReader(csv_file)
                    model.objects.bulk_create(model(**data) for data in reader)
            self.stdout.write(self.style.SUCCESS(
                'Data from all CSV files was successfully imported into '
                'database.'
            ))
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(e))
