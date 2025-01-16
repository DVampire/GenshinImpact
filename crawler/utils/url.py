def add_url(href: str) -> str:
    """
    Add the domain name to the URL
    :param href: str
    :return: str
    """
    if href.startswith('http') or href.startswith('https'):
        return href
    elif '无' in href:
        return ''
    else:
        return f'https://bbs.mihoyo.com{href}'
