from logging import getLogger

from django.core.management.base import BaseCommand

from sites.helpers.ThreadManager.ThreadManager import ThreadManager
from sites.models import Link, Page, Site, Image, PageData

logger = getLogger(__name__)


class Command(BaseCommand):
    help = 'Starts the crawler.'

    def add_arguments(self, parser):
        """
        Define positional and optional arguments to manage.py call.
        """
        pass

    def handle(self, *args, **options):
        """
        Entry point of our crawler, runs the thread manager.
        """
        print("Cleaning database...")
        print(Link.objects.all().delete())
        print(Page.objects.all().delete())
        print(Site.objects.all().delete())
        print(Image.objects.all().delete())
        print(PageData.objects.all().delete())
        print("Database brand spanking clean.")
