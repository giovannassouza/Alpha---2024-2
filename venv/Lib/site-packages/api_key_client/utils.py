from hashlib import md5
from datetime import datetime


def sort_query_string(query_string):
    lower_query_string = query_string.lower()
    sorted_query_string = ''.join(sorted(lower_query_string.split('&')))
    return sorted_query_string


def sign_request(url, api_secret, timestamp=None):
    """sign an url with api_key param"""
    timestamp = timestamp or datetime.now().strftime("%Y%m%d%H%M%S")
    if url.find('api_key') == -1:
        return 'please provide api_key field in url query string'
    query_string = url.split('?')[1]
    sorted_query_string = sort_query_string(query_string)
    data = f"{sorted_query_string}timestamp={timestamp}api_secret={api_secret}"
    sign = md5(data.encode('utf-8')).hexdigest()
    url += '&timestamp={}&sign={}'.format(timestamp, sign)
    return url


def sign_request_1(url, api_key, api_secret, timestamp=None):
    """sign an url providing api_key and api_secret """
    # print('original url:', url)
    url = url + "?api_key={}".format(api_key)
    return sign_request(url, api_secret, timestamp)
