import string
import random
import re


def id_generator(size: int = 6, chars=string.ascii_letters):
    return ''.join(random.choice(chars) for _ in range(size))


regex = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def is_valid_url(s: str) -> bool:
    """
    Returns true if s is valid http url, else false
    Arguments:
    """
    return bool(re.match(regex, s))
