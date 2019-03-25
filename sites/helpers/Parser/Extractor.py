from logging import getLogger

from bs4 import BeautifulSoup

logger = getLogger(__name__)

class Extractor:
    """
    This class is used to extract data from different sources.
    Extracted data is unmodified. List of urls that is returned must be validated (to append domain url,...)
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
        soup = BeautifulSoup(html_content, 'lxml')
        return soup.prettify()

    def parse_urls(self, html_content):
        """
        This function extracts all urls from html
        :param html_content: html content to parse
        :return: array of URLs
        """
        bs = BeautifulSoup(html_content, "lxml")
        urls = []

        for url in bs.find_all('a', href=True):
            urls.append(url['href'])
        return urls

    def parse_img_urls(self, html_content):
        """
        This function extracts all img urls from html
        :param html_content: html content to parse
        :return: array of img URLs
        """
        bs = BeautifulSoup(html_content, 'lxml')
        urls = []

        for img in bs.find_all('img'):
            urls.append(img['src'])
        return urls

    def parse_sitemap(self, xml):
        """
        This function is used for parsing sitemap
        :param xml: XML content to parse
        :return: List of found urls
        """
        urls = []

        if xml is None:
            return urls

        bs = BeautifulSoup(xml)
        sitemap_tags = bs.find_all("sitemap")

        logger.info("Extractor|\tThe number of sitemaps are {0}".format(len(sitemap_tags)))

        # return [sitemap.findNext('loc').text for sitemap in sitemap_tags]
        for sitemap in sitemap_tags:
            # find next url in sitemap
            url = sitemap.findNext("loc").text
            # logger.info(url)
            urls.append(url)
        return urls


if __name__ == "__main__":
    # Init class
    e = Extractor()

    html_doc = """
    <html><head><title>The Dormouse's story</title></head>
    <body>
    <p class="title"><b>The Dormouse's story</b></p>
    
    <p class="story">Once upon a time there were three little sisters; and their names were
    <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
    <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
    <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
    and they lived at the bottom of a well.</p>
    
    <p class="story">...</p><span>đčšžćčđščžćšč
    
    <img src="www.ful-dobra-slika.tmp" />
    
    """

    clean_html = e.clean_html(html_doc)
    # logger.info(clean_html)

    a = e.parse_urls(clean_html)
    logger.info(a)

    img_url = e.parse_img_urls(clean_html)
    logger.info(img_url)
