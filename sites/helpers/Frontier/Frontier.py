from logging import getLogger
from queue import Queue, Empty
from urllib.parse import urlparse

from sites.helpers.Downloader.HttpDownloader import HttpDownloader
from sites.models import Page, Link, Site, PageType

logger = getLogger(__name__)


class Frontier:

    def __init__(self, http_downloader=HttpDownloader(), initial_url_seed=[], restore=True):
        self.queue = Queue()
        self.http_downloader = http_downloader

        # Initial seed URLs
        if not restore:
            logger.info("Starting from inital seed.")
            for u in initial_url_seed:
                self.add_url(u)
        else:
            logger.info("Resuming from frontier.")

        if restore:
            # restore data from DB on init
            self.restore_frontier_from_db()

    def add_url(self, new_url, from_page=None, delay=4):
        """
        This function adds potentially new page to frontier and creates new empty page entry with code "FRONTIER"
        :param delay: number of second to delay crawler
        :param new_url: full url of potentially new page (string) to be added to frontier
        :type new_url: str
        :param from_page: page that url was found on
        :type from_page: Page
        :return: value that indicates whether url was added to frontier
        :rtype: bool
        """
        if Page.objects.filter(url=new_url).exists():
            return False

        netloc = urlparse(new_url).netloc

        # Create new site if it doesn't exist yet
        try:
            site = Site.objects.get(domain=netloc)
        except Site.DoesNotExist:
            # Download robots and sitemap
            sitemap_content, _ = self.http_downloader.get_sitemap_for_url("http://" + netloc, True)
            robots_content, _ = self.http_downloader.get_robots_file("http://" + netloc, True)
            # Save new site
            site = Site(domain=netloc, sitemap_content=sitemap_content, robots_content=robots_content)
            site.save()

        page_type = PageType.objects.get(code="FRONTIER")
        page = Page(url=new_url, site=site, page_type_code=page_type, crawl_delay=delay)
        page.save()

        # Create link if valid from_page was given
        if from_page:
            try:
                link = Link(from_page=from_page, to_page=page)
                link.save()
            except ValueError:
                logger.error("from_page must be valid Page instance")

        self.queue.put(page)
        return True

    def get_url(self):
        """
        Fetches url from frontier
        :return: Returns url from frontier and indicator whether frontier is empty
        :rtype: (str, bool)
        """
        try:
            return self.queue.get_nowait(), False
        except Empty:
            return None, True

    def restore_frontier_from_db(self):
        """
        This function restores frontier from db after possible unexpected program fail
        :return:
        """
        page_type = PageType.objects.get(code="FRONTIER")
        q = Page.objects.filter(page_type_code=page_type)

        for page in q:
            self.queue.put(page)
        pass
