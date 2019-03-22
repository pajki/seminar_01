import requests
from urllib.robotparser import RobotFileParser


class HttpDownloader:
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
        :return: response object
        """
        response = requests.head(url, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
        print('status code:', response.status_code)
        print('url:', response.url)
        print('headers:', response.headers)
        return response

    def get(self, url):
        """
        Create GET request to passed URL
        :param url: Url for request
        :return: response object
        """
        response = requests.get(url, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
        return response

    def get_page_body(self, url):
        """
        This function creates GET request and returns page body
        :param url:
        :return: Web page content
        """
        print('\nGet page body for URL:', url)
        response = requests.get(url, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)

        # check status code
        # TODO handle error codes
        if response.status_code is 200:
            print('Status code: ', response.status_code)
            return response.text, response.status_code
        else:
            print('Status code: ', response.status_code)
            return None, response.status_code

    def get_sitemap_for_url(self, base_url, append_file_name=False):
        """
        This function retrieves sitemap for specified url address
        :param base_url: Base url address
        :param append_file_name: append /robots.txt if True
        :return: XML content
        """
        path = base_url
        if append_file_name:
            path += '/sitemap.xml'

        print('GET sitemap.xml for %s' % path)
        response = requests.get(path, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
        if response.status_code is not 200:
            print('ERROR: sitemap.xml not found for %s' % path)
            return None
        # got sitemap
        return response.text

    def get_robots_file(self, base_url, append_file_name=False):
        """
        This function retrieves robots file for specified url address
        :param base_url: Base url address
        :param append_file_name: append /robots.txt if True
        :return: robots.txt content and status code
        """
        path = base_url
        if append_file_name:
            path += '/robots.txt'

        print('GET robots.txt for %s' % path)
        try:
            response = requests.get(path, verify=self.verify, allow_redirects=self.allow_redirects, timeout=self.timeout)
            if response.status_code is not 200:
                print('ERROR: robots.txt not found for %s' % path)
            return response.text, response.status_code
        except Exception as e:
            print("ERR: %s" % e)

        return None, None


if __name__ == "__main__":
    # url samples
    # django server base page
    url1 = 'http://127.0.0.1:8000/'

    # init class
    downloader = HttpDownloader()

    # simple tests
    body = downloader.get_page_body(url1)
    # print(body)

    sitemap = downloader.get_sitemap_for_url('https://google.com', True)
    print(sitemap)

    robots = downloader.get_robots_file('http://www.najdi.si/robots.txt')
    print(robots)

