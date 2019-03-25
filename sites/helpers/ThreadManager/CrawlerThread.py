from logging import getLogger
from threading import Thread

from sites.helpers.Crawler.Crawler import Crawler

logger = getLogger(__name__)


class CrawlerThread(Thread):

    def __init__(self, thread_id, frontier):
        """
        :param thread_id: id of the thread
        :param frontier: reference to the frontier objects
        """
        logger.info("Crawler thread {} initialized.".format(thread_id))
        Thread.__init__(self)
        self.thread_id = thread_id
        self.crawler = Crawler(frontier)

    def run(self):
        """
        Start thread and start crawling.
        """
        logger.info("Thread {} started.".format(self.thread_id))
        self.crawler.run()
        logger.info("Thread {} ended.".format(self.thread_id))
