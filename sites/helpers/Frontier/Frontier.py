from queue import LifoQueue
from urllib.parse import urldefrag, urlparse

from sites.helpers.Downloader.HttpDownloader import HttpDownloader

from sites.models import Page, Link, Site, PageType


class Frontier:

    def __init__(self, http_downloader=HttpDownloader()):
        self.queue = LifoQueue()
        self.http_downloader = http_downloader

    def add_url(self, new_url, from_page):
        """
        This function adds potentially new page to frontier and creates new empty page entry
        :param new_url: full url of potentially new page (string) to be added to frontier
        :param from_page: id of page which url was found on
        :return: returns boolean value that indicates weather url was added to frontier
        """

        # Remove fragment and add http:// if no scheme in url
        new_url = urldefrag(new_url).url
        if not urlparse(new_url).scheme:
            new_url = "http://" + new_url

        if Page.objects.filter(url=new_url).exists():
            return False

        # TODO .gov.si check
        # TODO canonical check
        # TODO duplicate invhash check

        netloc = urlparse(new_url).netloc

        # Create new site if it doesn't exist yet
        try:
            site = Site.objects.get(domain=netloc)
        except Site.DoesNotExist:
            site = Site(domain=netloc,
                        sitemap_content=self.http_downloader.get_sitemap_for_url("http://" + netloc, True),
                        robots_content=self.http_downloader.get_robots_file("http://" + netloc, True))
            site.save()

        page_type = PageType.objects.get(code="FRONTIER")
        page = Page(url=new_url, site=site, page_type_code=page_type)
        page.save()

        try:
            link = Link(from_page=from_page, to_page=page)
            link.save()
        except ValueError:
            print("ERR: from_page must be valid Page instance")

        self.queue.put(page)

        return True

    def get_url(self):
        # TODO
        return
