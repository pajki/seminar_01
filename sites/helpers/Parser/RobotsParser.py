from urllib.request import urlopen
import urllib.robotparser as robotparser
from urllib.error import *

from sites.helpers.Downloader.HttpDownloader import HttpDownloader


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
    def __init__(self, url):
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
        self.rp.set_url(self.page_url)
        print("setting url %s" % self.page_url)

        # request and read robots file
        try:
            # read file
            self.rp.read()

            # sets the time the robots.txt file was last fetched to the current time.
            self.rp.modified()

            self.file_exists = True
        except URLError as e:
            print("\nERROR\nMsg:\tCan't read robots file")
            print("URL:\t%s" % self.page_url)
            if hasattr(e, 'code'):
                print("Code:\t%s" % e.code)
            if hasattr(e, 'reason'):
                print("Reason:\t%s" % e.reason)

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
        except Exception as e:
            print("ERR: get_crawl_delay:\n%s" % e)
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
        except Exception as e:
            print("ERR: get_request_rate:\n%s" % e)
        return request_rate

    def check_if_can_fetch(self, url, useragent="*"):
        """
        Returns True if the useragent is allowed to fetch the url according to the rules
        contained in the parsed robots.txt file.
        :param url: url to check
        :param useragent: useragent -> defaults to *, leave it
        :return: Boolean
        """
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
            print("\nERROR\nMsg:\tCan't get robots content for database")
            print("URL:\t%s" % robots_url)
            if hasattr(e, 'code'):
                print("Code:\t%s" % e.code)
            if hasattr(e, 'reason'):
                print("Reason:\t%s" % e.reason)

        return self.content

    def get_robots_content(self):
        """
        Use downloader class to download robots content
        :return:
        """
        downloader = HttpDownloader()
        self.content, self.status_code = downloader.get_robots_file(base_url=self.page_url)
        return self.content, self.status_code

    def parse_sitemap_url_in_robots_file(self):
        """
        Convert robots.txt file content to lowercase and extract sitemaps urls
        :return:
        """
        if self.content is None:
            print("WARNING: No robots.txt content. Did we download it?")
            return []
        r_content = self.content.lower()
        return [url.strip() for url in r_content.split("sitemap: ")[1:]]

    def set_robots_content(self, new_content):
        """
        If we have robots.txt content in database use this function to set it
        :param new_content: robots content from database
        :return:
        """
        self.content = new_content
        self.status_code = 200


if __name__ == "__main__":
    print("main RobotsParser")
    local_url = "http://127.0.0.1:8000"
    # init
    r = RobotsParser(local_url)

    # parse robots
    r_exists = r.parse_robots_file()
    print("Robots file exists: %s" % r_exists)

    # test delay
    delay = r.get_crawl_delay()
    print("delay: %s" % delay)

    # test request rate
    rate = r.get_request_rate()
    print("request rate: %s" % rate)

    # download robots content
    content = r.get_robots_content()
    # print(content)

    # check if sitemap url exists in robots.txt
    s_url = r.parse_sitemap_url_in_robots_file()
    print("Sitemap url: %s" % s_url)
