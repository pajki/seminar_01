from urllib.parse import urldefrag, urlparse, urljoin


class UrlUtils:
    pass


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

    if only_gov_si and not url_is_gov_si(url_parsed.netloc):
        return None

    url = urldefrag(url).url

    #TODO check for more weird urls..

    return url


def url_is_gov_si(domain):

    return domain[-7:] == ".gov.si"

