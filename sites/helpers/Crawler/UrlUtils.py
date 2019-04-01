from urllib.parse import urldefrag, urlparse, urljoin
import re


class UrlUtils:
    pass


def get_domain(url):
    return "http://" + urlparse(url).netloc


def fix_image_url(url, caller_url):
    allowed_domains = ["www.evem.gov.si", "www.e-uprava.gov.si", "www.podatki.gov.si", "www.e-prostor.gov.si"]
    valid_url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(valid_url_regex, url) is not None:
        url = urljoin(caller_url, url, False)

    url_parsed = urlparse(url)
    if not url_parsed.scheme:
        url = "http://" + url

    # if url_parsed.netloc in allowed_domains:
    #     return url
    #
    # return None
    return url


def url_fix_relative(url, caller_url, only_gov_si=True):
    """
    Returns fixed absolute url string
    :param only_gov_si: return only gov.si urls, else None
    :param url: newly found url
    :param caller_url: caller url
    :return: fixed url or None
    """

    url = urljoin(caller_url, url, False)

    url_parsed = urlparse(url)
    if not url_parsed.scheme:
        url = "http://" + url

    allowed_extensions = ["aspx", "axd", "asx", "asmx", "ashx", "cfm", "yaws", "swf", "html", "htm", "xhtml", "jhtml",
                          "jsp", "jspx", "do", "action", "js", "pl", "php", "php4", "php3", "phtml", "py", "rb",
                          "rhtml", "shtml", "xml"]

    if len(url_parsed.path.split(".")) != 1:
        if url_parsed.path.split(".")[-1] not in allowed_extensions:
            return None

    if only_gov_si and not url_is_gov_si(url_parsed.netloc):
        return None

    url = urldefrag(url).url

    # TODO check for more weird urls..

    return url


def url_is_gov_si(domain):
    return domain[-7:] == ".gov.si"
