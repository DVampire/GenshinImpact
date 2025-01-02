from bs4 import BeautifulSoup


def save_html_file(html_content: str, path: str):
    """save html to file"""
    soup = BeautifulSoup(html_content, 'html.parser')
    formatted_html = soup.prettify()

    with open(path, 'w') as file:
        file.write(formatted_html)
