from sites.helpers.Downloader.HttpDownloader import HttpDownloader
from sites.helpers.Parser.RobotsParser import RobotsParser
from sites.helpers.Parser.Extractor import Extractor
from sites.helpers.Utils.LoggerHelper import init_logger, log


class Crawler:
    def __init__(self, frontier):
        self.frontier = frontier
        self.downloader = HttpDownloader()
        self.extractor = Extractor()
        self.robotParser = None
        init_logger(True)

    def run(self):
        log("---------------------------------------------------------------------------------------------")
        log("Running crawler")
        # [GLOBALS]
        robots_sitemap_urls = []
        all_urls = []
        crawl_delay = None
        request_rate = None

        # [FRONTIER]
        log("Getting element from frontier")
        page, empty = self.frontier.get_url()

        if empty:
            log("Frontier is empty %s" % empty)
            # TODO: tell thread manager that frontier is empty -> put this instance to sleep
            return empty

        if not empty:
            current_url = page.url
            log("Got obj from frontier %s" % current_url)

            # [HTML]
            log("\n[HTML]")
            log("Downloading page HTML")
            html_content, http_status_code = self.downloader.get_page_body(current_url)
            # TODO: do we need to handle http status codes?

            # clean html content
            log("Cleaning HTML")
            cleaned_html = self.extractor.clean_html(html_content)
            # log("HTML content\n%s" % cleaned_html)

            # parse URLs
            log("Parsing URLs")
            a_url = self.extractor.parse_urls(cleaned_html)
            log("Extracted URLs from <a> tag %s" % a_url)
            all_urls += self.extractor.parse_urls(cleaned_html)

            # [IMAGE]
            # log("\n[IMAGE]")
            # TODO: extract all images from web page and save them to DB

            # [ROBOTS]
            log("\n[ROBOTS]")
            # check if robots content exists in DB
            robots_content = page.site.robots_content
            if robots_content:
                log("Handle robots.txt")
                self.robotParser = RobotsParser(current_url)
                self.robotParser.set_robots_content(robots_content)
                self.robotParser.parse_robots_file()

                # [SITEMAP EXTRACTION]
                robots_sitemap_urls = self.robotParser.parse_sitemap_url_in_robots_file()
                log("List of sitemaps in robots %s" % robots_sitemap_urls)

                # [CRAWL DELAY] TODO: how do we handle this
                crawl_delay = self.robotParser.get_crawl_delay()
                if crawl_delay:
                    log("Got crawl delay from robots %s" % crawl_delay)

                # [REQUEST RATE] TODO: how do we handle this
                request_rate = self.robotParser.get_request_rate()
                if request_rate:
                    log("Got request rate from robots %s" % request_rate)
            else:
                log("Robots not found")

            # [SITEMAP]
            log("\n[SITEMAP]")
            # Check for defined sitemaps in robots.txt
            for sitemap_url in robots_sitemap_urls:
                log("Downloading sitemap for %s" % sitemap_url)
                content = self.downloader.get_sitemap_for_url(sitemap_url)
                s_urls = self.extractor.parse_sitemap(content)
                log("Appending sitemap urls to all urls %s" % s_urls)
                all_urls += s_urls

            # Check if sitemap exists in DB
            sitemap_content = page.site.sitemap_content
            if sitemap_content:
                sitemap_urls = self.extractor.parse_sitemap(sitemap_content)
                log("Parsed sitemap from DB, found %s" % sitemap_urls)
            else:
                log("Sitemap not found")

            # [URL]
            log("\n[URL]")
            log("Extracted %d urls" % len(all_urls))
            # TODO: our extractor extracts data from html. Not all URLs are in correct format. We need to handle those.
            # TODO: write URL helper class to handle urls

            # remove disallowed urls (check in robots.txt)
            if robots_content:
                log("Removing disallowed URLs")
                for u in all_urls:
                    if self.robotParser.check_if_can_fetch(u):
                        all_urls.append(u)

            # [EXTRACT additional data types -> PDF, etc.]
            # TODO extract additional documents and save them to DB

            # [SAVE DATA TO DB]

            # [UPDATE FRONTIER]

            # [GET NEW URL from FRONTIER]


if __name__ == "__main__":
    print("Run crawler instance")
    crawler = Crawler(None)
    crawler.run()




