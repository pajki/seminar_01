from logging import getLogger
from datetime import datetime
from sites.helpers.Downloader.HttpDownloader import HttpDownloader
from sites.helpers.Parser.RobotsParser import RobotsParser
from sites.helpers.Parser.Extractor import Extractor
from sites.models import PageType

logger = getLogger(__name__)


class Crawler:
    def __init__(self, frontier):
        self.frontier = frontier
        self.downloader = HttpDownloader()
        self.extractor = Extractor()
        self.robotParser = None

    def save_to_db(self, page, http_code, html_content):
        page_type = PageType.objects.get(code="HTML")
        page.page_type_code = page_type
        page.http_status_code = http_code
        page.html_content = html_content
        page.accessed_time = datetime.now()
        page.save()

    def save_img_url_to_db(self):
        """
        # TODO
        :return:
        """
        pass

    def save_document_to_db(self):
        """
        # TODO
        :return:
        """
        pass

    def run(self):
        logger.info("---------------------------------------------------------------------------------------------")
        logger.info("Running crawler")
        # [GLOBALS]
        robots_sitemap_urls = []
        all_urls = []
        crawl_delay = None
        request_rate = None

        # [FRONTIER]
        logger.info("Getting element from frontier")
        page, empty = self.frontier.get_url()

        if empty:
            logger.info("Frontier is empty %s" % empty)
            # TODO: tell thread manager that frontier is empty -> put this instance to sleep
            return empty

        if not empty:
            current_url = page.url
            logger.info("Got obj from frontier %s" % current_url)

            # [HTML]
            logger.info("[HTML]")
            logger.info("Downloading page HTML")
            html_content, http_status_code = self.downloader.get_page_body(current_url)
            # TODO: do we need to handle http status codes?

            # clean html content
            logger.info("Cleaning HTML")
            cleaned_html = self.extractor.clean_html(html_content)
            # logger.info("HTML content\n%s" % cleaned_html)

            # parse URLs
            logger.info("Parsing URLs")
            a_url = self.extractor.parse_urls(cleaned_html)
            logger.info("Extracted URLs from <a> tag %s" % a_url)
            all_urls += self.extractor.parse_urls(cleaned_html)

            # [IMAGE]
            logger.info("[IMAGE]")
            # TODO: fix extracted URLs & save extracted images to DB
            image_urls = self.extractor.parse_img_urls(cleaned_html)

            # [EXTRACT additional data types -> PDF, etc.]
            logger.info("[FILES]")
            # TODO extract additional documents and save them to DB
            document_urls = self.extractor.parse_files(cleaned_html)

            # [ROBOTS]
            logger.info("[ROBOTS]")
            # check if robots content exists in DB
            robots_content = page.site.robots_content
            if robots_content:
                logger.info("Handle robots.txt")
                self.robotParser = RobotsParser(current_url)
                self.robotParser.set_robots_content(robots_content)
                self.robotParser.parse_robots_file()

                # [SITEMAP EXTRACTION]
                robots_sitemap_urls = self.robotParser.parse_sitemap_url_in_robots_file()
                logger.info("List of sitemaps in robots %s" % robots_sitemap_urls)

                # [CRAWL DELAY] TODO: how do we handle this
                crawl_delay = self.robotParser.get_crawl_delay()
                if crawl_delay:
                    logger.info("Got crawl delay from robots %s" % crawl_delay)

                # [REQUEST RATE] TODO: how do we handle this
                request_rate = self.robotParser.get_request_rate()
                if request_rate:
                    logger.info("Got request rate from robots %s" % request_rate)

                # HOW TO HANDLE REQUEST RATE AND CRAWL DELAY
                """
                In page table we have accessed time attr. Use that time to determine if we can crawl this page
                """
            else:
                logger.info("Robots not found")

            # [SITEMAP]
            logger.info("[SITEMAP]")
            # Check for defined sitemaps in robots.txt
            for sitemap_url in robots_sitemap_urls:
                logger.info("Downloading sitemap for %s" % sitemap_url)
                content = self.downloader.get_sitemap_for_url(sitemap_url)
                s_urls = self.extractor.parse_sitemap(content)
                logger.info("Appending sitemap urls to all urls %s" % s_urls)
                all_urls += s_urls

            # Check if sitemap exists in DB
            sitemap_content = page.site.sitemap_content
            if sitemap_content:
                sitemap_urls = self.extractor.parse_sitemap(sitemap_content)
                logger.info("Parsed sitemap from DB, found %s" % sitemap_urls)
            else:
                logger.info("Sitemap not found")

            # [URL]
            logger.info("[URL]")
            logger.info("Extracted %d urls" % len(all_urls))
            # TODO: our extractor extracts data from html. Not all URLs are in correct format. We need to handle those.
            # TODO: write URL helper class to handle urls

            # remove disallowed urls (check in robots.txt)
            filtered_urls = []
            if robots_content:
                logger.info("Removing disallowed URLs")
                for u in all_urls:
                    if self.robotParser.check_if_can_fetch(u):
                        filtered_urls.append(u)

            # [SAVE DATA TO DB]
            logger.info("[DATABASE]")
            # update page entry
            logger.info("saving page")
            self.save_to_db(page, http_status_code, cleaned_html)
            # save images
            logger.info("saving img")
            self.save_img_url_to_db()
            # save additional documents
            logger.info("saving documents")
            self.save_document_to_db()

            # [UPDATE FRONTIER]
            for u in filtered_urls:
                self.frontier.add_url(new_url=u, from_page=current_url)

            # [GET NEW URL from FRONTIER]


if __name__ == "__main__":
    logger.info("Run crawler instance")
    crawler = Crawler(None)
    crawler.run()




