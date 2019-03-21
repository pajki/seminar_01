
from sites.helpers.Downloader.HttpDownloader import HttpDownloader
from sites.helpers.Parser.RobotsParser import RobotsParser
from sites.helpers.Parser.Extractor import Extractor


class Crawler:
    def __init__(self, frontier):
        self.frontier = frontier
        self.downloader = HttpDownloader()
        self.extractor = Extractor()
        self.robotParser = None

    def run(self):
        # local vars
        sitemap_url = None
        image_urls = []
        html_content_urls = []

        # get url from frontier and PK for db entry
        # url, primary_key = self.frontier.get_url()
        # current_url = 'http://127.0.0.1:8000'
        current_url = 'http://evem.gov.si'

        # init
        self.robotParser = RobotsParser(current_url)

        # HEAD request for URL ??
        head_request = self.downloader.head(current_url)

        # check for robots.txt
        robots_file_exists = self.robotParser.parse_robots_file()
        print("Robots file exists: ", robots_file_exists)

        if robots_file_exists:
            # download robots content
            self.robotParser.get_robots_content()

            # check for sitemap
            sitemap_url = self.robotParser.check_for_sitemap_url()
            print("Found sitemap url", sitemap_url)

            # check request rate
            request_rate = self.robotParser.get_request_rate()
            print("request rate", request_rate)

            # check crawl delay
            crawler_delay = self.robotParser.get_crawl_delay()
            print("crawler delay", crawler_delay)

        # download sitemap content
        if sitemap_url is not None:
            # sitemap obtained from robots.txt
            sitemap_xml = self.downloader.get_sitemap_for_url(sitemap_url)
        else:
            sitemap_xml = self.downloader.get_sitemap_for_url(current_url, True)

        # Extract sitemap urls
        sitemap_urls = self.extractor.parse_sitemap(sitemap_xml)
        print("Sitemap urls: ", sitemap_urls)

        # GET request for page content
        page_html_content = self.downloader.get_page_body(current_url)
        # print(page_html_content)
        # TODO: handle error codes
        if page_html_content is None:
            # use headles browser
            print("TODO: headless browser")
        else:
            # clean HTML
            # page_html_content = self.extractor.clean_html(page_html_content)

            # find all ULRs on page
            html_content_urls = self.extractor.parse_urls(page_html_content)
            print("Html urls: ", html_content_urls)
            # use headless browser if needed

            # find images
            image_urls = self.extractor.parse_img_urls(page_html_content, current_url)
            print("Image urls: ", image_urls)

        combined = sitemap_urls + image_urls + html_content_urls
        print("All urls: ", combined)

        # remove not allowed urls (check in robots.txt)
        all_urls = []
        if robots_file_exists:
            for u in combined:
                if self.robotParser.check_if_can_fetch(u):
                    all_urls.append(u)

        print("Allowed urls: ", all_urls)
        # add viable URLs to frontier

        # select new url

        # dodajanje novih urljev v frontir -> new url and (current url || PK page entitete)
        pass


if __name__ == "__main__":
    print("Run crawler instance")
    crawler = Crawler(None)
    crawler.run()


