from abc import ABC, abstractmethod
from typing import Optional

from playwright.async_api import Page

__all__ = ['AbstractParser']


class AbstractParser(ABC):
    @abstractmethod
    async def parse(self, page: Optional[Page] = None) -> None:
        """
        parse page
        :param page:
        :return:
        """
        pass
