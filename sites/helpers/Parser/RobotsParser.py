from urllib.request import urlopen
import urllib.robotparser as robotparser
from urllib.error import *


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
    def __init__(self):
        self.rp = robotparser.RobotFileParser()
        self.content = None

    def parse_robots_file(self, page_url):
        """
        Get robots.txt file for page.
        Check url structure and append robots.txt to the url.

        :param page_url: page URL
        """
        # check url structure
        robots_url = check_robots_url(page_url)

        # set robots url to fetch
        self.rp.set_url(robots_url)

        # request and read robots file
        try:
            # read file
            self.rp.read()

            # sets the time the robots.txt file was last fetched to the current time.
            self.rp.modified()

        except URLError as e:
            print("\nERROR\nMsg:\tCan't read robots file")
            print("URL:\t%s" % robots_url)
            if hasattr(e, 'code'):
                print("Code:\t%s" % e.code)
            if hasattr(e, 'reason'):
                print("Reason:\t%s" % e.reason)

    def get_crawl_delay(self, useragent="*"):
        """
        Returns the value of the Crawl-delay parameter from robots.txt for the useragent
        :param useragent:
        :return: delay or None
        """
        crawl_delay = None
        try:
            crawl_delay = self.rp.crawl_delay(useragent=useragent)
        except:
            pass
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
        except:
            pass
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

    def get_robots_content(self, page_url, encoding="utf-8"):
        """
        Download robots.txt content
        :param page_url: url to download from
        :param encoding: file encoding
        :return:
        """
        robots_url = check_robots_url(page_url)

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

    def check_for_sitemap_url(self):
        """
        Check if sitemap is defined in robots.txt file. If it exists return URL.
        :return: Sitemap URL or None
        """
        sitemap_url = None

        if self.content is None:
            return None

        if "Sitemap" in self.content:
            sitemap_url = self.content.split('Sitemap: ')[1]
        elif "sitemap" in self.content:
            sitemap_url = self.content.split('sitemap: ')[1]
        return sitemap_url


if __name__ == "__main__":
    print("main RobotsParser")
    local_url = "http://127.0.0.1:8000/robots.txt"
    # init
    r = RobotsParser()

    # parse robots
    r.parse_robots_file(page_url=local_url)

    # test delay
    delay = r.get_crawl_delay()
    print("delay: %s" % delay)

    # test request rate
    rate = r.get_request_rate()
    print("request rate: %s" % rate)

    # download robots content
    content = r.get_robots_content(local_url)
    # print(content)

    # check if sitemap url exists in robots.txt
    s_url = r.check_for_sitemap_url()
    print("Sitemap url: %s" % s_url)


