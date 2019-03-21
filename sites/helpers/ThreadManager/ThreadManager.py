from sites.helpers.ThreadManager.CrawlerThread import CrawlerThread


class ThreadManager:

    def __init__(self, thread_num):
        """
        :param thread_num: number of threads to start.
        """
        self.thread_num = thread_num
        # self.frontier = Frontier()
        self.frontier = None

    def run(self):
        """
        Start self.thread_num of threads.
        """
        for i in range(0, self.thread_num):
            crawler_thread = CrawlerThread(i, self.frontier)
            crawler_thread.start()
