from threading import Thread
from time import sleep

from sites.helpers.Crawler.Crawler import Crawler


class CrawlerThread(Thread):

    def __init__(self, thread_id, frontier):
        """
        :param thread_id: id of the thread
        :param frontier: reference to the frontier objects
        """
        print("Crawler thread {} initialized.".format(thread_id))
        Thread.__init__(self)
        self.thread_id = thread_id
        self.crawler = Crawler(frontier)

    def run(self):
        """
        Start thread and start crawling.
        """
        print("Thread {} started.".format(self.thread_id))
        self.crawler.run()
        print("Thread {} ended.".format(self.thread_id))
