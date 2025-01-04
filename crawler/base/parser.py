import os
from abc import ABC, abstractmethod
from typing import Optional

from playwright.async_api import BrowserContext, Page

from crawler.utils.html_files import save_html_file
from crawler.utils.screenshot import scroll_and_capture

__all__ = ['AbstractParser']


class AbstractParser(ABC):
    img_path: str
    html_path: str

    @abstractmethod
    async def parse(self) -> None:
        """
        parse page
        :param page:
        :return:
        """
        pass

    async def _save_screenshot(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
        sleep_time: int = 1,
        remove_header: bool = True,
        remove_footer: bool = False,
        viewport_height_adjustment: int = 0,
    ) -> None:
        save_name = f'{0:04d}_full'

        # Save a screenshot of the page
        await scroll_and_capture(
            context_page,
            os.path.join(self.img_path, f'{save_name}.png'),
            sleep_time=sleep_time,
            remove_header=remove_header,
            remove_footer=remove_footer,
            viewport_height_adjustment=viewport_height_adjustment,
        )

        # Get the page content
        content = await context_page.content()  # type: ignore

        # Save the HTML content to a file
        save_html_file(content, os.path.join(self.html_path, f'{save_name}.html'))
