import time
import threading

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Starts the crawler.'

    def add_arguments(self, parser):
        parser.add_argument('concurrency', type=int)

    def handle(self, *args, **options):
        print("This is the entry point of our crawler.")
        print("Starting {} crawlers...".format(options['concurrency']))
