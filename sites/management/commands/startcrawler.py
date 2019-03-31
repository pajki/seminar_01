from datetime import datetime
from logging import getLogger

import pytz
from django.core.management.base import BaseCommand

from sites.helpers.ThreadManager.ThreadManager import ThreadManager

logger = getLogger(__name__)


class Command(BaseCommand):
    help = 'Starts the crawler.'

    def add_arguments(self, parser):
        """
        Define positional and optional arguments to manage.py call.
        """
        parser.add_argument('concurrency', type=int)

        parser.add_argument('--restore', action='store_true', dest='restore', help='Restore from frontier.')

    def handle(self, *args, **options):
        """
        Entry point of our crawler, runs the thread manager.
        """
        s = datetime.now(tz=pytz.UTC)
        logger.info("Starting time: {}".format(s))
        logger.info("Starting thread manager...")
        if options['restore']:
            thread_manager = ThreadManager(options["concurrency"], True)
        else:
            thread_manager = ThreadManager(options["concurrency"], False)
        thread_manager.run()
        e = datetime.now(tz=pytz.UTC)
        logger.info("Stopping time: {}".format(e))
        logger.info("Total running time: {}".format(e - s))
