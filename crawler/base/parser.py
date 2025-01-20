import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page

from crawler.logger import logger
from crawler.utils.html_files import save_html_file
from crawler.utils.screenshot import scroll_and_capture

__all__ = ['AbstractParser']


class AbstractParser(ABC):
    def __init__(
        self,
        *args,
        config,
        url: str,
        id: str,
        name: str,
        img_path: str,
        html_path: str,
        icon: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.config = config
        self.url = url
        self.id = id
        self.name = name
        self.icon = icon

        self.img_path = img_path
        self.html_path = html_path

        self.save_id = 0

        self.save_screen = self.config.save_screen

    @abstractmethod
    async def _parse(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        """
        Parse the page
        :param context_page:
        :return:
        """
        raise NotImplementedError

    async def parse(
        self,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        parse page
        :param page:
        :return:
        """
        res_info: Dict[str, Any] = dict()

        # New a context page
        context_page = await browser_context.new_page()

        logger.info(f'| Go to the page {self.url}')
        # Open the page
        await context_page.goto(self.url)

        try:
            # Ensure all network activity is complete
            await context_page.wait_for_load_state('networkidle')
        except Exception as e:
            logger.info(f'｜ Error: {e}')

        logger.info('| Start parsing page...')
        save_name = f'{self.save_id:04d}_full'
        self.save_id += 1

        self.img_path = os.path.join(self.img_path, self.id)
        os.makedirs(self.img_path, exist_ok=True)
        self.html_path = os.path.join(self.html_path, self.id)
        os.makedirs(self.html_path, exist_ok=True)

        # Save a screenshot of the page
        content, img_path, html_path = await self._save_screenshot(
            context_page=context_page,
            save_name=save_name,
            browser_context=browser_context,
            save_screen=self.save_screen,
        )

        # Save the results to the dictionary
        res_info['url'] = self.url
        res_info['id'] = self.id
        res_info['name'] = self.name
        res_info['icon'] = self.icon
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path

        logger.info('| Start parsing page - sub elements...')

        # Parse the page
        res_info['data'] = await self._parse(context_page, browser_context)

        logger.info('| Finish parsing page - sub elements...')

        logger.info('| Finish parsing page...')

        # Close the context page
        await context_page.close()

        return res_info

    async def _save_screenshot(
        self,
        context_page: Optional[Page] = None,
        save_name: str = f'{0:04d}_full',
        browser_context: Optional[BrowserContext] = None,
        sleep_time: int = 1,
        remove_header: bool = True,
        remove_footer: bool = False,
        viewport_height_adjustment: int = 0,
        save_screen: bool = False,
    ):
        img_path = os.path.join(self.img_path, f'{save_name}.png')
        html_path = os.path.join(self.html_path, f'{save_name}.html')

        # Save a screenshot of the page
        if save_screen:
            await scroll_and_capture(
                context_page,
                img_path,
                sleep_time=sleep_time,
                remove_header=remove_header,
                remove_footer=remove_footer,
                viewport_height_adjustment=viewport_height_adjustment,
            )

        # Get the page content
        content = await context_page.content()  # type: ignore

        # Save the HTML content to a file
        if save_screen:
            save_html_file(content, html_path)

        return content, img_path, html_path
