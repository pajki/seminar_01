from logging import getLogger
from random import randint
from time import sleep

from django.conf import settings

from sites.helpers.ThreadManager.CrawlerThread import CrawlerThread
from sites.helpers.Frontier.Frontier import Frontier

logger = getLogger(__name__)


class ThreadManager:

    def __init__(self, thread_num):
        """
        :param thread_num: number of threads to start.
        """
        self.threads = []
        self.thread_num = thread_num
        # self.frontier = Frontier(initial_url_seed=["evem.gov.si/evem/drzavljani/zacetna.evem", "e-uprava.gov.si"])
        self.frontier = Frontier(initial_url_seed=["evem.gov.si/evem/drzavljani/zacetna.evem"], )

    def run(self):
        """
        Start self.thread_num of threads and then manage their execution.
        """
        logger.info("Initializing threads...")
        for i in range(0, self.thread_num):
            crawler_thread = CrawlerThread(i, self.frontier)
            crawler_thread.start()
            self.threads.append(crawler_thread)
        logger.info("Threads initialized.")

        # Do thread management and end when there are not more URLs to parse.
        try:
            while True:
                sleeping_threads = 0
                logger.info("Checking for sleeping threads...")
                for thread in self.threads:
                    if thread.is_sleeping():
                        sleeping_threads += 1
                        logger.info("Thread {} is asleep.".format(thread.thread_id))

                if sleeping_threads == self.thread_num:
                    logger.info("Our work here is done. Stopping all threads and exiting.")
                    for thread in self.threads:
                        logger.info("Joining thread {}.".format(thread.thread_id))
                        thread.join()
                    logger.info("Goodbye.")
                    return self.thread_num

                timeout = int(settings.CRAWLER_THREAD_TIMEOUT / 4 + randint(-3, 3))
                logger.info("{} out of {} threads are asleep. Checking again in {} seconds.".format(
                    sleeping_threads, self.thread_num, timeout))
                sleep(timeout)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt initiated.")
            logger.info("Stopping threads...")
            for thread in self.threads:
                thread.join()
                logger.info("Thread {} stopped.".format(thread.thread_id))
            logger.info("All threads stopped, goodbye.")
            return self.thread_num
