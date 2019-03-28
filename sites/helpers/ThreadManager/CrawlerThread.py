from logging import getLogger
from threading import Thread
from time import sleep

from django.conf import settings

from sites.helpers.Crawler.Crawler import Crawler

logger = getLogger(__name__)


class CrawlerThread(Thread):

    def __init__(self, thread_id, frontier, add_url_lock):
        """
        :param thread_id: id of the thread
        :param frontier: reference to the frontier objects
        """
        logger.info("Crawler thread {} initialized.".format(thread_id))
        Thread.__init__(self)
        self.thread_id = thread_id
        self.crawler = Crawler(frontier, add_url_lock)
        self.asleep = False
        self.kill = False

    def run(self):
        """
        Start thread and start crawling. If there are no new urls,
        sleep for CRAWLER_THREAD_TIMEOUT seconds, set in settings.py.
        """
        logger.info("Thread {} started.".format(self.thread_id))

        while True:
            try:
                result = self.crawler.run()
            except Exception as e:
                logger.info("Error occurred while running a crawler instance.")
                logger.error(e)
                logger.info("Restarting the crawler thread...")
                continue

            # If kill attribute was set to True, return from thread
            if self.kill:
                logger.info("Killing thread {}".format(self.thread_id))
                return 420
            # If we got an URL as a result, continue with the crawling
            if result:
                continue

            # If the result we received was None, the frontier is empty - go to sleep and then resume
            logger.info("No new URLS, thread {} sleeping for {} seconds.".format(
                self.thread_id, settings.CRAWLER_THREAD_TIMEOUT
            ))
            self.asleep = True
            sleep(settings.CRAWLER_THREAD_TIMEOUT)
            self.asleep = False
            logger.info("Thread {} resuming.".format(self.thread_id))

    def is_sleeping(self):
        """
        Return the value of self.asleep to tell if the thread is sleeping.
        """
        return self.asleep

    def kill_thread(self):
        """
        Set kill flag to True.
        """
        self.kill = True
