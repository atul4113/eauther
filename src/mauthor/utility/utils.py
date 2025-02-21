import re


def sanitize_title(title):
    """
    Sanitize entity title from prohibited characters - new lines and tabulators.

    :param title: entity title to be sanitized
    :type title: str|unicode
    :return: sanitized title without prohibited characters
    :rtype: str|unicode
    """
    return re.sub('[\t\n\r]', '', title)