from logging import getLogger

from sites.helpers.ThreadManager.CrawlerThread import CrawlerThread
from sites.helpers.Frontier.Frontier import Frontier

logger = getLogger(__name__)


class ThreadManager:

    def __init__(self, thread_num):
        """
        :param thread_num: number of threads to start.
        """
        self.thread_num = thread_num
        self.frontier = Frontier(initial_url_seed=["evem.gov.si/evem/drzavljani/zacetna.evem", "e-uprava.gov.si"])

    def run(self):
        """
        Start self.thread_num of threads.
        """
        logger.info("Initializing threads...")
        for i in range(0, self.thread_num):
            crawler_thread = CrawlerThread(i, self.frontier)
            crawler_thread.start()
