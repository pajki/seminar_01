from logging import getLogger
from queue import LifoQueue, Empty
from urllib.parse import urldefrag, urlparse

from sites.helpers.Downloader.HttpDownloader import HttpDownloader

from sites.models import Page, Link, Site, PageType

logger = getLogger(__name__)


class Frontier:

    def __init__(self, http_downloader=HttpDownloader(), gov_si_only=True, initial_url_seed=[]):
        self.queue = LifoQueue()
        self.http_downloader = http_downloader
        self.gov_si_only = gov_si_only
        # Initial seed URLs
        for u in initial_url_seed:
            self.add_url(u)

        # restore data from DB on init
        # self.restore_frontier_from_db()

    def add_url(self, new_url, from_page=None):
        """
        This function adds potentially new page to frontier and creates new empty page entry with code "FRONTIER"
        :param new_url: full url of potentially new page (string) to be added to frontier
        :type new_url: str
        :param from_page: page that url was found on
        :type from_page: Page
        :return: value that indicates whether url was added to frontier
        :rtype: bool
        """
        # Remove fragment and add http:// if no scheme in url
        new_url = urldefrag(new_url).url
        if not urlparse(new_url).scheme:
            new_url = "http://" + new_url

        if Page.objects.filter(url=new_url).exists():
            return False

        # TODO canonical check
        # TODO duplicate invhash check

        netloc = urlparse(new_url).netloc

        # TODO maybe check if url string contains gov.si instead of splitting to arr (might have problem with index)
        if self.gov_si_only:
            netloc_split = netloc.split(".")
            if netloc_split[-2] != "gov" or netloc_split[-1] != "si":
                return False

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
        page = Page(url=new_url, site=site, page_type_code=page_type)
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
