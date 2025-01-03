import os
from typing import Any, Dict, Optional

from playwright.async_api import Page

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.html_files import save_html_file
from crawler.utils.screenshot import scroll_and_capture

__all__ = [
    'SummonParser',
]


class SummonParser(AbstractParser):
    def __init__(self, config, url: str, page_name='wiki') -> None:
        self.config = config
        self.url = url
        self.page_name = page_name

    async def parse(self, page: Optional[Page] = None) -> Dict[str, Any]:
        """
        parse page
        :param page:
        :return:
        """
        logger.info(f'| Go to the page {self.url}')
        # Open the page
        await page.goto(self.url)

        # Ensure all network activity is complete
        await page.wait_for_load_state('networkidle')

        logger.info('| Start parsing page...')

        self.img_path = os.path.join(self.config.img_path, self.page_name)
        os.makedirs(self.img_path, exist_ok=True)
        self.html_path = os.path.join(self.config.html_path, self.page_name)
        os.makedirs(self.html_path, exist_ok=True)

        # Save a screenshot of the page
        await self._save_screenshot(
            page
        )  # TODO: Comment it out for now, as this method causes the page to scroll, which slows down the speed.

        # Parse the page
        res_info = await self._parse(page)

        logger.info('| Finish parsing page...')

        return res_info

    async def _save_screenshot(self, page: Optional[Page] = None) -> None:
        save_name = f'{0:04d}_full'

        # Save a screenshot of the page
        await scroll_and_capture(page, os.path.join(self.img_path, f'{save_name}.png'))

        # Get the page content
        content = await page.content()  # type: ignore

        # Save the HTML content to a file
        save_html_file(content, os.path.join(self.html_path, f'{save_name}.html'))

    async def _parse(self, page: Optional[Page] = None) -> Dict[str, Any]:
        """
        :param page:
        :return: res_info: Dict[str, Any]
        """

        res_info: Dict[str, Any] = dict()

        return res_info
