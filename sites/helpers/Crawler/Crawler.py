from logging import getLogger

from sites.helpers.Downloader.HttpDownloader import HttpDownloader
from sites.helpers.Parser.RobotsParser import RobotsParser
from sites.helpers.Parser.Extractor import Extractor
from sites.helpers.Crawler.UrlUtils import url_fix_relative

logger = getLogger(__name__)


class Crawler:
    def __init__(self, frontier):
        self.frontier = frontier
        self.downloader = HttpDownloader(allow_redirects=False)
        self.extractor = Extractor()
        self.robotParser = None

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
            logger.info("\n[HTML]")
            logger.info("Downloading page HTML")
            html_content, http_status_code = self.downloader.get_page_body(current_url)
            # TODO: do we need to handle http status codes?

            # clean html content
            logger.info("Cleaning HTML")
            cleaned_html = self.extractor.clean_html(html_content)
            # logger.info("HTML content\n%s" % cleaned_html)

            # parse URLs
            logger.info("Parsing URLs")
            all_urls += self.extractor.parse_urls(cleaned_html)

            # [IMAGE]
            # logger.info("\n[IMAGE]")
            # TODO: extract all images from web page and save them to DB

            # [ROBOTS]
            logger.info("\n[ROBOTS]")
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
            else:
                logger.info("Robots not found")

            # [SITEMAP]
            logger.info("\n[SITEMAP]")
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
                all_urls += sitemap_content
            else:
                logger.info("Sitemap not found")

            # [URL]
            logger.info("\n[URL]")
            logger.info("Extracted %d urls" % len(all_urls))
            # TODO: our extractor extracts data from html. Not all URLs are in correct format. We need to handle those.
            # TODO: write URL helper class to handle urls

            filtered_urls = []
            # remove disallowed urls (check in robots.txt)
            if robots_content:
                logger.info("Removing disallowed URLs")
                for u in all_urls:
                    if self.robotParser.check_if_can_fetch(u):
                        filtered_urls.append(u)
            else:
                filtered_urls = all_urls

            for u in filtered_urls:
                tmp_url = url_fix_relative(u, current_url)
                if tmp_url:
                    self.frontier.add_url(from_page=page, new_url=tmp_url)

            # [EXTRACT additional data types -> PDF, etc.]
            # TODO extract additional documents and save them to DB

            # [SAVE DATA TO DB]

            # [UPDATE FRONTIER]

            # [GET NEW URL from FRONTIER]
            self.run()


if __name__ == "__main__":
    logger.info("Run crawler instance")
    crawler = Crawler(None)
    crawler.run()




