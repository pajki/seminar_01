from logging import getLogger
from time import sleep
from django.utils import timezone
from sites.helpers.Downloader.HttpDownloader import HttpDownloader
from sites.helpers.Parser.RobotsParser import RobotsParser
from sites.helpers.Parser.Extractor import Extractor
from sites.models import PageType
from sites.helpers.Crawler.UrlUtils import url_fix_relative, fix_file_url, get_domain

logger = getLogger(__name__)


class Crawler:
    def __init__(self, frontier, add_url_lock):
        self.frontier = frontier
        self.downloader = HttpDownloader(allow_redirects=False)
        self.extractor = Extractor()
        self.robotParser = None
        self.add_url_lock = add_url_lock

    @staticmethod
    def update_current_page_entry(page, http_code, html_content):
        """
        Update current page entry in DB
        :param page: page obj
        :param http_code: status code
        :param html_content: received content
        :return: None
        """
        page.page_type_code = PageType.objects.get(code="HTML")
        page.http_status_code = http_code
        page.html_content = html_content
        page.accessed_time = timezone.now()
        logger.info("Saving page {}...".format(page.url))
        page.save()
        logger.info("Paged {} saved.".format(page.url))

    def run(self):
        logger.info("\n---------------------------------------------------------------------------------------------")
        logger.info("Running crawler")
        # [GLOBALS]
        robots_sitemap_urls = []
        all_urls = []

        # default crawl delay is 4 s
        crawl_delay = None
        request_rate = None

        # [FRONTIER]
        logger.info("Getting element from frontier")
        page, empty = self.frontier.get_url()

        if empty:
            logger.info("Frontier is empty %s" % empty)
            return None

        if not empty:
            current_url = page.url
            domain = get_domain(current_url)
            logger.info("Got obj from frontier %s" % current_url)
            logger.info("Domain %s" % domain)

            # [CRAWL DELAY]
            # get crawl delay for page
            delay = page.crawl_delay
            logger.info("Waiting crawl delay %s for %s" % (delay, current_url))
            sleep(delay)

            # [HTML]
            logger.info("[HTML]")
            logger.info("Downloading page HTML")
            html_content, http_status_code = self.downloader.get_page_body(current_url)
            logger.info("Status code: [%s]" % http_status_code)

            # no HTML content was received, return and crawl new url
            if not html_content or http_status_code == 404:
                logger.info("No html, stop crawling %s" % current_url)
                self.add_url_lock.acquire()
                try:
                    # update page entry
                    logger.info("updating page page")
                    self.update_current_page_entry(page, http_status_code, html_content)
                finally:
                    self.add_url_lock.release()
                print("No content for %s " % current_url)
                return current_url

            # clean html content
            logger.info("Cleaning HTML")
            cleaned_html = self.extractor.clean_html(html_content)
            # logger.info("HTML content\n%s" % cleaned_html)

            # parse URLs
            logger.info("Parsing URLs")
            all_urls += self.extractor.parse_urls(cleaned_html)

            # [IMAGE]
            logger.info("[IMAGE]")
            image_urls = self.extractor.parse_img_urls(cleaned_html)
            logger.info("Found %d img urls" % len(image_urls))

            # [FILES]
            logger.info("[FILES]")
            document_urls = self.extractor.parse_files(cleaned_html)
            logger.info("Found %d documents" % len(document_urls))

            # [ROBOTS]
            logger.info("[ROBOTS]")
            # check if robots content exists in DB
            robots_content = page.site.robots_content
            if robots_content:
                logger.info("Handle robots.txt")
                try:
                    self.robotParser = RobotsParser(domain)
                    self.robotParser.set_robots_content(robots_content)
                    self.robotParser.parse_robots_file()

                    # [SITEMAP EXTRACTION]
                    robots_sitemap_urls = self.robotParser.parse_sitemap_url_in_robots_file()
                    logger.info("List of sitemaps in robots %s" % robots_sitemap_urls)

                    # [CRAWL DELAY]
                    crawl_delay = self.robotParser.get_crawl_delay()
                    if request_rate:
                        logger.info("Got crawl delay from robots %s" % crawl_delay)

                    # [REQUEST RATE]
                    request_rate = self.robotParser.get_request_rate()
                    if request_rate:
                        logger.info("Got request rate from robots %s" % request_rate)

                    # HOW TO HANDLE REQUEST RATE AND CRAWL DELAY
                except:
                    logger.info("Error reading robots")
            else:
                logger.info("Robots not found")

            # [SITEMAP]
            logger.info("[SITEMAP]")
            # Check for defined sitemaps in robots.txt
            for sitemap_url in robots_sitemap_urls:
                logger.info("Downloading sitemap for %s" % sitemap_url)
                content, _ = self.downloader.get_sitemap_for_url(sitemap_url)
                s_urls = self.extractor.parse_sitemap(content)
                logger.info("Appending sitemap urls to all urls %s" % len(s_urls))
                all_urls += s_urls

            # Check if sitemap exists in DB
            sitemap_content = page.site.sitemap_content
            if sitemap_content:
                sitemap_urls = self.extractor.parse_sitemap(sitemap_content)
                logger.info("Parsed sitemap from DB, found %s" % len(sitemap_urls))
                all_urls += sitemap_content
            else:
                logger.info("Sitemap not found")

            # [URL]
            logger.info("[URL]")
            logger.info("Extracted %d urls" % len(all_urls))

            # remove disallowed urls (check in robots.txt)
            filtered_urls = []
            if robots_content:
                logger.info("Removing disallowed URLs")
                for u in all_urls:
                    if self.robotParser.check_if_can_fetch(u):
                        filtered_urls.append(u)
            else:
                filtered_urls = all_urls

            logger.info("Acquiring lock")
            self.add_url_lock.acquire()
            logger.info("Lock acquired")
            try:
                # [SAVE DATA TO DB]
                logger.info("[DATABASE]")
                # update page entry
                logger.info("saving page")
                self.update_current_page_entry(page, http_status_code, cleaned_html)

                if len(filtered_urls) > 500:
                    logger.info("Skipping to much to handle")
                    return current_url

                logger.info("Adding items to frontier")
                # [UPDATE FRONTIER]
                # Add filtered URLs to frontier
                for u in filtered_urls:
                    tmp_url = url_fix_relative(u, current_url)
                    if tmp_url:
                        if crawl_delay:
                            self.frontier.add_url(from_page=page, new_url=tmp_url, delay=crawl_delay)
                        else:
                            self.frontier.add_url(from_page=page, new_url=tmp_url)

                logger.info("Frontier updated")
                # [SAVE IMAGES]
                logger.info("Saving images")
                for u in image_urls:
                    tmp_url = fix_file_url(u, current_url)
                    if tmp_url:
                        self.downloader.download_file_and_save_image_file(tmp_url, page.id)
                logger.info("Done")
                # [SAVE FILES]
                logger.info("Saving files")
                for u in document_urls:
                    tmp_url = fix_file_url(u, current_url)
                    if tmp_url:
                        self.downloader.download_file_and_save(tmp_url, page.id)
                logger.info("Done")
            finally:
                logger.info("Releasing lock")
                self.add_url_lock.release()
                logger.info("Lock released")

            print("Extracted: {} urls from {}".format(len(filtered_urls), current_url))

            return current_url


if __name__ == "__main__":
    logger.info("Run crawler instance")
