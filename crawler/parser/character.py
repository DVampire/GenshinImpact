import asyncio
import os
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page

from crawler.base import AbstractParser
from crawler.logger import logger

__all__ = [
    'CharacterParser',
]


class CharacterParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        page_name: str,
        character_name: str,
        icon: str,
        img_path: str,
        html_path: str,
        **kwargs,
    ) -> None:
        self.config = config
        self.url = url
        self.page_name = page_name
        self.character_name = character_name
        self.icon = icon

        self.img_path = img_path
        self.html_path = html_path

    async def parse(
        self,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        parse page
        :param context_page:
        :return:
        """
        # New a context page
        context_page = await browser_context.new_page()

        logger.info(f'| Go to the page {self.url}')
        # Open the page
        await context_page.goto(self.url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')
        await asyncio.sleep(1)

        logger.info('| Start parsing page...')

        self.img_path = os.path.join(self.img_path, self.page_name)
        os.makedirs(self.img_path, exist_ok=True)
        self.html_path = os.path.join(self.html_path, self.page_name)
        os.makedirs(self.html_path, exist_ok=True)

        # Save a screenshot of the page
        await self._save_screenshot(
            context_page,
            browser_context,
            sleep_time=2,
            remove_header=True,
            remove_footer=True,
            viewport_height_adjustment=-70,
        )  # TODO: Comment it out for now, as this method causes the page to scroll, which slows down the speed.

        # Parse the page
        res_info = await self._parse(context_page, browser_context)

        logger.info('| Finish parsing page...')

        # Close the context page
        await context_page.close()

        return res_info

    async def _parse(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        :param page:
        :return: res_info: Dict[str, Any]
        """

        res_info: Dict[str, Any] = dict()

        return res_info
