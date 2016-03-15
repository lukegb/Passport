from urllib.parse import urlparse
import unicodedata

def is_safe_host(hostname):
    return hostname in ('spongepowered.org', 'localhost:5000') or hostname.endswith('.spongepowered.org')


# the below are from django (https://github.com/django/django/blob/552f03869ea7f3072b3fa19ffb6cb2d957fd8447/django/utils/http.py)
def is_safe_url(url, host=None):
    """
    Return ``True`` if the url is a safe redirection (i.e. it doesn't point to
    a different host and uses a safe scheme).
    Always returns ``False`` on an empty url.
    """
    if url is not None:
        url = url.strip()
    if not url:
        return False
    # Chrome treats \ completely as / in paths but it could be part of some
    # basic auth credentials so we need to check both URLs.
    return _is_safe_url(url, host) and _is_safe_url(url.replace('\\', '/'), host)


def _is_safe_url(url, host):
    # Chrome considers any URL with more than two slashes to be absolute, but
    # urlparse is not so flexible. Treat any url with three slashes as unsafe.
    if url.startswith('///'):
        return False
    url_info = urlparse(url)
    # Forbid URLs like http:///example.com - with a scheme, but without a hostname.
    # In that URL, example.com is not the hostname but, a path component. However,
    # Chrome will still consider example.com to be the hostname, so we must not
    # allow this syntax.
    if not url_info.netloc and url_info.scheme:
        return False
    # Forbid URLs that start with control characters. Some browsers (like
    # Chrome) ignore quite a few control characters at the start of a
    # URL and might consider the URL as scheme relative.
    if unicodedata.category(url[0])[0] == 'C':
        return False
    return ((not url_info.netloc or is_safe_host(url_info.netloc)) and
            (not url_info.scheme or url_info.scheme in ['http', 'https']))
