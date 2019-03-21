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

    def clean_html(self, html_content):
        """
        Clean html
        TODO: we might need to handle file encoding
        Time consuming!
        :param html_content: html content to clean
        :return: cleaned content
        """
        tree = BeautifulSoup(html_content)
        return tree.prettify()

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

    def parse_img_urls(self, html_content, base_url):
        """
        This function extracts all img urls from html
        :param html_content: html content to parse
        :return: array of img URLs
        """
        bs = BeautifulSoup(html_content)
        urls = []

        for img in bs.find_all('img'):
            url = base_url + img['src']
            print("Found image URL:", url)
            urls.append(url)
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

        # return [sitemap.findNext('loc').text for sitemap in sitemap_tags]
        for sitemap in sitemap_tags:
            # find next url in sitemap
            url = sitemap.findNext("loc").text
            # print(url)
            urls.append(url)
        return urls


if __name__ == "__main__":
    # url samples
    # django test page
    url1 = 'http://127.0.0.1:8000'
    url2 = 'https://www.google.si'

    # Init classes
    e = Extractor()
    d = HttpDownloader()

    # Test url parser
    content = d.get_page_body(url1)
    e.parse_urls(content)

    # get google landing page and parse img
    content2 = d.get_page_body(url2)
    e.parse_img_urls(content2, url2)

    # Test sitemap parser
    xml_content = d.get_sitemap_for_url(url1, True)
    sitemap_urls = e.parse_sitemap(xml_content)
    print(sitemap_urls)

    # Link(from_page='asd', to_page='bsd').save()
