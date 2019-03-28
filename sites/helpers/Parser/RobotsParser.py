from logging import getLogger
from urllib.request import urlopen
import urllib.robotparser as robotparser
from urllib.error import *

from sites.helpers.Downloader.HttpDownloader import HttpDownloader

logger = getLogger(__name__)

def check_robots_url(url):
    """
    Check url structure and append robots.txt if needed
    :param url:
    :return: URL with robots.txt
    """
    robots_url = str(url)
    if "robots.txt" not in robots_url and not robots_url.endswith("/"):
        robots_url += "/"

    if "robots.txt" not in robots_url:
        robots_url += "robots.txt"
    return robots_url


class RobotsParser:
    def __init__(self, url, debug=False):
        self.rp = robotparser.RobotFileParser()
        self.page_url = check_robots_url(url)
        self.content = None
        self.file_exists = False
        self.status_code = 0

    def parse_robots_file(self):
        """
        Get robots.txt file for page.
        Check url structure and append robots.txt to the url.
        Return True if robots exists
        :return Boolean
        """
        self.file_exists = False

        # set robots url to fetch
        logger.info("RobotParser|\tSetting url %s for robot parser" % self.page_url)
        self.rp.set_url(self.page_url)

        # request and read robots file
        try:
            logger.info("RobotParser|\tReading robots file")
            # read file
            self.rp.read()
            logger.info("RobotParser|\tContent saved in robot parser")
            # sets the time the robots.txt file was last fetched to the current time.
            self.rp.modified()

            self.file_exists = True
        except URLError as e:
            logger.error("Can't read robots file.")
            logger.error("URL:\t%s" % self.page_url)
            if hasattr(e, 'code'):
                logger.error("Code:\t%s" % e.code)
            if hasattr(e, 'reason'):
                logger.error("Reason:\t%s" % e.reason)

        return self.file_exists

    def get_crawl_delay(self, useragent="*"):
        """
        Returns the value of the Crawl-delay parameter from robots.txt for the useragent
        :param useragent:
        :return: delay or None
        """
        crawl_delay = None
        try:
            crawl_delay = self.rp.crawl_delay(useragent=useragent)
            logger.info("RobotParser|\tCrawl delay is %s" % crawl_delay)
        except Exception as e:
            logger.error("get_crawl_delay:\n%s" % e)

        if not crawl_delay:
            return 4
        return crawl_delay

    def get_request_rate(self, useragent="*"):
        """
        Returns the contents of the Request-rate parameter from robots.txt
        as a named tuple RequestRate(requests, seconds)
        :param useragent:
        :return: tuple RequestRate(requests, seconds) or None
        """
        request_rate = None
        try:
            request_rate = self.rp.request_rate(useragent=useragent)
            logger.info("RobotParser|\tRequest rate is %s" % request_rate)
        except Exception as e:
            logger.error("get_request_rate:\n%s" % e)
        return request_rate

    def check_if_can_fetch(self, url, useragent="*"):
        """
        Returns True if the useragent is allowed to fetch the url according to the rules
        contained in the parsed robots.txt file.
        :param url: url to check
        :param useragent: useragent -> defaults to *, leave it
        :return: Boolean
        """
        logger.debug("RobotParser|\tChecking if can fetch %s" % url)
        return self.rp.can_fetch(useragent=useragent, url=url)

    def get_robots_content2(self, encoding="utf-8"):
        """
        Download robots.txt content
        :param encoding: file encoding
        :return:
        """
        robots_url = check_robots_url(self.page_url)

        try:
            with urlopen(robots_url) as stream:
                self.content = stream.read().decode(encoding)
        except URLError as e:
            logger.error("Can't get robots content for database")
            logger.error("URL:\t%s" % robots_url)
            if hasattr(e, 'code'):
                logger.error("Code:\t%s" % e.code)
            if hasattr(e, 'reason'):
                logger.error("Reason:\t%s" % e.reason)

        return self.content

    def get_robots_content(self):
        """
        Use downloader class to download robots content
        :return:
        """
        logger.info("RobotParser|\tPreparing to download robots.txt content")
        downloader = HttpDownloader()
        self.content, self.status_code = downloader.get_robots_file(base_url=self.page_url)
        logger.info("RobotParser|\tGET robots.txt status code %s" % self.status_code)
        return self.content, self.status_code

    def parse_sitemap_url_in_robots_file(self):
        """
        Convert robots.txt file content to lowercase and extract sitemaps urls
        :return:
        """
        logger.info("RobotParser|\tparsing robots.txt content for sitemap urls")
        if self.content is None:
            logger.info("WARNING: No robots.txt content. Did we download it?")
            return []
        r_content = self.content.lower()
        return [url.strip() for url in r_content.split("sitemap: ")[1:]]

    def set_robots_content(self, new_content):
        """
        If we have robots.txt content in database use this function to set it
        :param new_content: robots content from database
        :return:
        """
        logger.info("RobotParser|\tSetting new content")
        self.content = new_content
        self.status_code = 200


if __name__ == "__main__":
    logger.info("main RobotsParser\n")
    local_url = "http://127.0.0.1:8000"
    # init
    r = RobotsParser(local_url, True)

    # parse robots
    r_exists = r.parse_robots_file()
    logger.info("Robots file exists: %s" % r_exists)

    # test delay
    delay = r.get_crawl_delay()
    logger.info("delay: %s" % delay)

    # test request rate
    rate = r.get_request_rate()
    logger.info("request rate: %s" % rate)

    # download robots content
    content = r.get_robots_content()
    # logger.info(content)

    # check if sitemap url exists in robots.txt
    s_url = r.parse_sitemap_url_in_robots_file()
    logger.info("Sitemap url: %s" % s_url)
