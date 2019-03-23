import requests
from urllib.robotparser import RobotFileParser
from sites.helpers.Utils.LoggerHelper import log, init_logger


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
        log('HttpDownloader|\tstatus code: %s' % response.status_code)
        log('HttpDownloader|\turl: %s' % response.url)
        log('HttpDownloader|\theaders: %s' % response.headers)
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
        log('HttpDownloader|\tGet page body for URL: %s' % url)
        response = requests.get(url, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)

        log('HttpDownloader|\tStatus code: %s' % response.status_code)
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

        log('HttpDownloader|\tGET sitemap.xml for %s' % path)
        try:
            response = requests.get(path, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
            headers = response.headers
            content_type = headers["content-type"]

            # check if response is in xml
            if (content_type == "application/xml" or content_type == "text/xml") and response.status_code == 200:
                log("HttpDownloader|\tFOUND sitemap.xml file")
                return response.text, response.status_code
            log("HttpDownloader|\tNO sitemap.xml file")
            return None, response.status_code
        except Exception as e:
            log("ERR: %s" % e)

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

        log('HttpDownloader|\tGET robots.txt for %s' % path)
        try:
            response = requests.get(path, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
            headers = response.headers
            content_type = headers["content-type"]

            # check if response is in text/plain
            if content_type == "text/plain" and response.status_code == 200:
                log("HttpDownloader|\tFOUND robots.txt file")
                return response.text, response.status_code

            log("HttpDownloader|\tNO robots.txt file")
            return None, response.status_code
        except Exception as e:
            log("ERR: %s" % e)

        return None, None


if __name__ == "__main__":
    # url samples
    # django server base page
    # url1 = 'http://127.0.0.1:8000/'
    init_logger(True)
    # init class
    downloader = HttpDownloader()

    # # simple tests
    # body = downloader.get_page_body(url1)
    # # log(body)
    #
    # sitemap = downloader.get_sitemap_for_url('https://google.com', True)
    # # print(sitemap)
    #
    robots, status = downloader.get_robots_file('http://www.najdi.si/robots.txt')
    print(robots)

    sitemap, status = downloader.get_robots_file('http://www.google.si', True)
    print(sitemap)
    #
    # a, status = downloader.head("http://evem.gov.si/robots.txt")
    # print(a.headers)
    #
    # a, status = downloader.head("http://google.si/robots.txt")
    # print(a.headers)
    #
    # a, status = downloader.head("http://google.si/sitemap.xml")
    # print(a.headers)
