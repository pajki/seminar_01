from bs4 import BeautifulSoup
# from sites.models import Link

# Custom classes
from sites.helpers.Downloader.HttpDownloader import HttpDownloader


class Extractor:
    """
    This class is used to extract data from different sources
    """
    def __init__(self):
        pass

    def parse_urls(self, html_content):
        """
        This function extracts all urls from html
        :param html_content: html content to parse
        :return: array of URLs
        """
        bs = BeautifulSoup(html_content)
        urls = []

        for url in bs.find_all('a', href=True):
            print("Found the URL:", url['href'])
            urls.append(url['href'])

        return urls

    def parse_sitemap(self, xml):
        """
        This function is used for parsing sitemap
        :param xml: XML content to parse
        :return: List of found urls
        """
        urls = []
        bs = BeautifulSoup(xml)
        sitemap_tags = bs.find_all("sitemap")

        print("The number of sitemaps are {0}".format(len(sitemap_tags)))
        for sitemap in sitemap_tags:
            # find next url in sitemap
            url = sitemap.findNext("loc").text
            # print(url)
            urls.append(url)
        return urls


    def parse_robots_file(self, content):
        """
        path = base_url
        if append_file_name:
            path += '/robots.txt'

        self.robot_parser.set_url(path)
        self.robot_parser.read()
        rrate = self.robot_parser.request_rate('*')
        print(rrate)
        print(self.robot_parser.crawl_delay('*'))
        """
        pass


if __name__ == "__main__":
    # url samples
    # django test page
    url1 = 'http://127.0.0.1:8000'

    # Init classes
    e = Extractor()
    d = HttpDownloader()

    # Test url parser
    e.parse_urls(d.get_page_body(url1))

    # Test sitemap parser
    sitemap_file = open('/home/gore/Workspace/ieps/seminar_01/test_files/sitemap.xml').read()
    sitemap_urls = e.parse_sitemap(sitemap_file)
    print(sitemap_urls)

    # Link(from_page='asd', to_page='bsd').save()
