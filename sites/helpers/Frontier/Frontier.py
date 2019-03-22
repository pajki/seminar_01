from queue import LifoQueue
from urllib.parse import urldefrag, urlparse
from django.db import IntegrityError

from sites.helpers.Downloader.HttpDownloader import HttpDownloader

from sites.models import Page, Link, Site


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
        new_url = urldefrag(new_url).url
        if Page.objects.exists(url=new_url):
            return False

        netloc = urlparse(new_url).netloc

        # Create new site if it doesn't exist yet
        if not Site.objects.exists(domain=netloc):
            site = Site(domain=netloc, sitemap_content=self.http_downloader.get_sitemap_for_url(netloc, True),
                        robots_content=self.http_downloader.get_robots_file(netloc, True))
            site.save()
        else:
            site = Site.objects.get(domain=netloc)

        try:
            page = Page.objects.create(url=new_url, site_id=site.id)
            link = Link.objects.create(from_page=from_page, to_page=page.id)

            self.queue.put((page.url, page.id))

        except IntegrityError as e:
            print(e)
            return False

        return True

    def get_url(self):
        # TODO
        return
