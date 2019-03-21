from django.core.management.base import BaseCommand

from sites.helpers.ThreadManager.ThreadManager import ThreadManager


class Command(BaseCommand):
    help = 'Starts the crawler.'

    def add_arguments(self, parser):
        """
        Define positional and optional arguments to manage.py call.
        """
        parser.add_argument('concurrency', type=int)

    def handle(self, *args, **options):
        """
        Entry point of our crawler, runs the thread manager.
        """
        print("Starting thread manager...")
        thread_manager = ThreadManager(options["concurrency"])
        thread_manager.run()
