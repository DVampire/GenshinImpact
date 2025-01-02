from typing import Optional

from playwright.async_api import Page

from crawler.base import AbstractParser

__all__ = [
    'IndexParser',
]


class IndexParser(AbstractParser):
    context_page: Page

    def __init__(self, context_page: Optional[Page] = None) -> None:
        self.context_page = context_page

    async def parse(self, page: Optional[Page] = None) -> None:
        """
        parse page
        :param page:
        :return:
        """
        if not page:
            page = self.context_page
