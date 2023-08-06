from django.core.management import BaseCommand
from django.conf import settings

from store.loader import ProductLoader



class Command(BaseCommand):
    help = "Load products from csv file"

    def handle(self, *args, **options):
        loader = ProductLoader(settings.PRODUCTS_CSV_PATH)
        loader.process()
