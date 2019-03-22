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

    def run(self):
        init_logger(True)

        log("---------------------------------------------------------------------------------------------")
        log("Running crawler")

        # local vars
        sitemap_url = None
        image_urls = []
        html_content_urls = []
        sitemap_urls = []

        # get url from frontier and PK for db entry
        # url, primary_key = self.frontier.get_url()
        # current_url = 'http://127.0.0.1:8000'
        current_url = 'http://evem.gov.si'
        log("Processing url: %s" % current_url)

        # init
        self.robotParser = RobotsParser(current_url)

        # HEAD request for URL ??
        log("\n[HEAD]")
        head_request = self.downloader.head(current_url)


        # check for robots.txt
        log("\n[ROBOTS]")
        robots_file_exists = self.robotParser.parse_robots_file()
        log("Robots file exists: %s" % robots_file_exists)

        if robots_file_exists:
            # download robots content
            self.robotParser.get_robots_content()

            # check for sitemap
            sitemap_url = self.robotParser.parse_sitemap_url_in_robots_file()
            log("Found sitemap url %s" % sitemap_url)

            # check request rate
            request_rate = self.robotParser.get_request_rate()
            log("request rate %s" % request_rate)

            # check crawl delay
            crawler_delay = self.robotParser.get_crawl_delay()
            log("crawler delay %s" % crawler_delay)

        # download sitemap content
        log("\n[SITEMAP]")
        if sitemap_url is not None:
            # sitemap obtained from robots.txt
            sitemap_xml = self.downloader.get_sitemap_for_url(sitemap_url)
        else:
            sitemap_xml = self.downloader.get_sitemap_for_url(current_url, True)

        # Extract sitemap urls
        sitemap_urls = self.extractor.parse_sitemap(sitemap_xml)
        log("Sitemap urls: %s" % sitemap_urls)

        # GET request for page content
        log("\n[HTML parsing]")
        page_html_content = self.downloader.get_page_body(current_url)
        # print(page_html_content)
        # TODO: handle error codes
        if page_html_content is None:
            # use headles browser
            log("TODO: headless browser")
        else:
            # clean HTML
            # page_html_content = self.extractor.clean_html(page_html_content)

            # find all ULRs on page
            # html_content_urls = self.extractor.parse_urls(page_html_content)
            log("Html urls: %s" % html_content_urls)
            # use headless browser if needed

            # find images
            #image_urls = self.extractor.parse_img_urls(page_html_content, current_url)
            log("Image urls: %s" % image_urls)

        combined = sitemap_urls + image_urls + html_content_urls
        log("All urls: %s" % combined)

        # remove not allowed urls (check in robots.txt)
        all_urls = []
        if robots_file_exists:
            for u in combined:
                if self.robotParser.check_if_can_fetch(u):
                    all_urls.append(u)

        log("Allowed urls: %s" % all_urls)
        # add viable URLs to frontier

        # select new url

        # dodajanje novih urljev v frontir -> new url and (current url || PK page entitete)
        pass


if __name__ == "__main__":
    print("Run crawler instance")
    crawler = Crawler(None)
    crawler.run()




