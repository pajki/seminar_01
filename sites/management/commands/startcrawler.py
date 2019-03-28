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

    def handle(self, *args, **options):
        """
        Entry point of our crawler, runs the thread manager.
        """
        s = datetime.now(tz=pytz.UTC)
        logger.info("Starting time: {}".format(s))
        logger.info("Starting thread manager...")
        thread_manager = ThreadManager(options["concurrency"])
        thread_manager.run()
        e = datetime.now(tz=pytz.UTC)
        logger.info("Stopping time: {}".format(e))
        logger.info("Total running time: {}".format(e - s))
