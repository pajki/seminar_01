import re
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
        logger.info("Extractor|\tCleaning html")
        return soup.prettify()

    def parse_urls(self, html_content):
        """
        This function extracts all urls from html
        :param html_content: html content to parse
        :return: array of URLs
        """
        bs = BeautifulSoup(html_content, "lxml")
        urls = []

        logger.info("Extractor|\tParsing urls from <a/>")
        # extract url from <a href={url} />
        urls += [url['href'] for url in bs.find_all('a', href=True)]

        logger.info("Extractor|\tParsing urls from location api")
        # extract url fromjs navigation API
        regex = r"location.assign\((.*)\)|location.replace\((.*)\)|location\.href\=\"(.*)\"|location\.href\=\'(.*)\'"
        matches = re.finditer(regex, html_content, re.MULTILINE)
        # black magic
        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                if match.group(groupNum):
                    urls.append(match.group(groupNum))
        logger.info("Extractor|\tFound %d" % len(urls))
        return urls

    def parse_img_urls(self, html_content):
        """
        This function extracts all img urls from html
        :param html_content: html content to parse
        :return: array of img URLs
        """
        bs = BeautifulSoup(html_content, 'lxml')
        urls = []
        logger.info("Extractor|\tParsing urls from <img>")
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

    def parse_files(self, html):
        """
        Extract files from html with regex expression
        :param html:
        :return:
        """
        logger.info("Extractor|\tParsing urls for files")
        files = re.findall('href="(.*pdf|.*doc|.*docx|.*ppt|.*pptx)"', html)
        return files


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
        
        <img src="/img/moja-slika.jpg" />
        <a href="/img/moja-slika.pdf" />
    
        <script>location.href="wwww.ful-dober-link-1.com"</script>
        <script>location.replace("wwww.ful-dober-link-2.com")</script>
        <script>location.assign("wwww.ful-dober-link-3.com")</script>
        
        <input type="button" onClick=location.assign("wwww.ful-dober-link-4.com")>click me</input>
        <script>location.href='wwww.ful-dober-link-5.com'</script>
        asd
        asea
        sd
        dsa
        d
        <p>asjdoiasdjhaso</p>
    """

    clean_html = e.clean_html(html_doc)
    # print(clean_html)

    a_url = e.parse_urls(clean_html)
    print(a_url)

    img_url = e.parse_img_urls(clean_html)
    print(img_url)

    print(e.parse_files(clean_html))
