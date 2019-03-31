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

    allowed_extensions = ["aspx","axd","asx","asmx","ashx","CSS","css","cfm","yaws","swf","html","htm","xhtml","jhtml",
                          "jsp","jspx","wss","do","action","js","pl","php","php4","php3","phtml","py","rb","rhtml",
                          "shtml","xml","rss","svg","cgi","dll"]

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
