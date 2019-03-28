from logging import getLogger

import requests
from urllib.robotparser import RobotFileParser

logger = getLogger(__name__)


class HttpDownloader:
    """
    This class provides methods for downloading different files/content.

    Every method returns content and status code
    """
    def __init__(self, verify=False, allow_redirects=True, timeout=50):
        # set default params
        self.verify = verify
        self.allow_redirects = allow_redirects
        self.timeout = timeout
        self.robot_parser = RobotFileParser()

    def head(self, url):
        """
        Create HEAD request to passed URL
        :param url: Url for request
        :return: response object and status code
        """
        response = requests.head(url, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
        logger.info('HttpDownloader|\tstatus code: %s' % response.status_code)
        logger.info('HttpDownloader|\turl: %s' % response.url)
        logger.info('HttpDownloader|\theaders: %s' % response.headers)
        return response, response.status_code

    def get(self, url):
        """
        Create GET request to passed URL
        :param url: Url for request
        :return: response object and status code
        """
        response = requests.get(url, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
        return response, response.status_code

    def get_page_body(self, url):
        """
        This function creates GET request and returns page body
        :param url: target URL
        :return: Web page content and status code
        """
        logger.info('HttpDownloader|\tGet page body for URL: %s' % url)
        response = requests.get(url, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)

        logger.info('HttpDownloader|\tStatus code: %s' % response.status_code)
        return response.text, response.status_code

    def get_sitemap_for_url(self, base_url, append_file_name=False):
        """
        This function retrieves sitemap for specified url address
        :param base_url: Base url address
        :param append_file_name: append /robots.txt if True
        :return: XML content and status code
        """
        path = base_url
        if append_file_name:
            path += '/sitemap.xml'

        logger.info('HttpDownloader|\tGET sitemap.xml for %s' % path)
        try:
            response = requests.get(path, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
            headers = response.headers
            content_type = headers["content-type"]

            # check if response is in xml
            if (content_type == "application/xml" or content_type == "text/xml") and response.status_code == 200:
                logger.info("HttpDownloader|\tFOUND sitemap.xml file")
                return response.text, response.status_code
            logger.info("HttpDownloader|\tNO sitemap.xml file")
            return None, response.status_code
        except Exception as e:
            logger.error(e)

        return None, None

    def get_robots_file(self, base_url, append_file_name=False):
        """
        This function retrieves robots file for specified url address
        If response is in text/plain then we know that content that we received is robots.txt file.
        Otherwise this method returns NOne

        :param base_url: Base url address
        :param append_file_name: append /robots.txt if True
        :return: robots.txt content and status code
        """
        path = base_url
        if append_file_name:
            path += '/robots.txt'

        logger.info('HttpDownloader|\tGET robots.txt for %s' % path)
        try:
            response = requests.get(path, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
            headers = response.headers
            content_type = headers["content-type"]

            # check if response is in text/plain
            if content_type == "text/plain" and response.status_code == 200:
                logger.info("HttpDownloader|\tFOUND robots.txt file")
                return response.text, response.status_code

            logger.info("HttpDownloader|\tNO robots.txt file")
            return None, response.status_code
        except Exception as e:
            logger.error(e)

        return None, None


if __name__ == "__main__":
    # url samples
    # django server base page
    # url1 = 'http://127.0.0.1:8000/'
    # init class
    downloader = HttpDownloader()

    # # simple tests
    # body = downloader.get_page_body(url1)
    # # logger.info(body)
    #
    # sitemap = downloader.get_sitemap_for_url('https://google.com', True)
    # # logger.info(sitemap)
    #
    robots, status = downloader.get_robots_file('http://www.najdi.si/robots.txt')
    logger.info(robots)

    sitemap, status = downloader.get_robots_file('http://www.google.si', True)
    logger.info(sitemap)
    #
    # a, status = downloader.head("http://evem.gov.si/robots.txt")
    # logger.info(a.headers)
    #
    # a, status = downloader.head("http://google.si/robots.txt")
    # logger.info(a.headers)
    #
    # a, status = downloader.head("http://google.si/sitemap.xml")
    # logger.info(a.headers)
