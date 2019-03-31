from logging import getLogger
from random import randint
from time import sleep
from threading import Lock

from django.conf import settings

from sites.helpers.ThreadManager.CrawlerThread import CrawlerThread
from sites.helpers.Frontier.Frontier import Frontier

logger = getLogger(__name__)

seed = ["http://www.evem.gov.si", "http://www.e-uprava.gov.si", "http://www.podatki.gov.si", "http://www.e-prostor.gov.si"]


class ThreadManager:

    def __init__(self, thread_num, restore=True):
        """
        :param thread_num: number of threads to start.
        """
        self.threads = []
        self.thread_num = thread_num
        self.frontier = Frontier(initial_url_seed=seed, restore=restore)
        self.url_add_lock = Lock()

    def run(self):
        """
        Start self.thread_num of threads and then manage their execution.
        """
        print("Initializing threads...")
        for i in range(0, self.thread_num):
            crawler_thread = CrawlerThread(i, self.frontier, self.url_add_lock)
            crawler_thread.start()
            self.threads.append(crawler_thread)
            # delay starting new threads
            sleep(1)
        print("Threads initialized.")

        # Do thread management and end when there are not more URLs to parse.
        try:
            while True:
                sleeping_threads = 0
                print("Checking for sleeping threads...")
                for thread in self.threads:
                    if thread.is_sleeping():
                        sleeping_threads += 1
                        print("Thread {} is asleep.".format(thread.thread_id))

                if sleeping_threads == self.thread_num:
                    print("Our work here is done. Stopping all threads and exiting.")
                    for thread in self.threads:
                        thread.kill_thread()
                    print("Goodbye.")
                    return self.thread_num

                timeout = int(settings.CRAWLER_THREAD_TIMEOUT / 2 + randint(-3, 3))
                print("{} out of {} threads are asleep. Checking again in {} seconds.".format(
                    sleeping_threads, self.thread_num, timeout))
                sleep(timeout)

        except KeyboardInterrupt:
            print("Keyboard interrupt initiated.")
            print("Killing threads...")
            for thread in self.threads:
                thread.kill_thread()
            print("Goodbye.")
            return self.thread_num
