import os
from typing import Any, Dict, List, Optional

from playwright.async_api import Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.html_files import save_html_file
from crawler.utils.screenshot import scroll_and_capture

__all__ = [
    'IndexParser',
]


class IndexParser(AbstractParser):
    def __init__(self, config) -> None:
        self.config = config

    async def parse(self, page: Optional[Page] = None) -> None:
        """
        parse page
        :param page:
        :return:
        """
        logger.info('| Start parsing index page...')

        self.img_path = os.path.join(self.config.img_path, 'index')
        os.makedirs(self.img_path, exist_ok=True)
        self.html_path = os.path.join(self.config.html_path, 'index')
        os.makedirs(self.html_path, exist_ok=True)

        # Save a screenshot of the page
        # await self._save_screenshot(page) # TODO: Comment it out for now, as this method causes the page to scroll, which slows down the speed.

        # Parse quick navigation
        await self._parse_quick_navigation(page)

    async def _save_screenshot(self, page: Optional[Page] = None) -> None:
        save_name = f'{0:04d}_full'

        # Save a screenshot of the page
        await scroll_and_capture(page, os.path.join(self.img_path, f'{save_name}.png'))

        # Get the page content
        content = await page.content()  # type: ignore

        # Save the HTML content to a file
        save_html_file(content, os.path.join(self.html_path, f'{save_name}.html'))

    async def _parse_quick_navigation(
        self, page: Optional[Page] = None
    ) -> Dict[str, Any]:
        """
        :param page:
        :return: res_info: Dict[str, Any] = dict(element_img_path: str, element_html_path: str, element_data: List[Dict[str, Any]])
        """

        res_info: Dict[str, Any] = dict()

        ###################################Get the element##########################################
        logger.info('| Start parsing index - quick navigation - element...')
        save_name = f'{1:04d}_quick_navigation'
        class_name = 'ul.home__map'

        # Wait for the element to load
        await page.wait_for_selector(class_name)  # type: ignore

        # Locate the first matching element
        element = page.locator(class_name).first  # type: ignore

        # Capture a screenshot of the element
        image = await element.screenshot()

        # Save the screenshot to a file
        with open(os.path.join(self.img_path, f'{save_name}.png'), 'wb') as file:
            file.write(image)

        # Get the inner HTML of the element
        content = await element.evaluate('el => el.outerHTML')

        # Save the HTML content to a file
        save_html_file(content, os.path.join(self.html_path, f'{save_name}.html'))

        # Save the results to the dictionary
        res_info['element_img_path'] = os.path.join(self.img_path, f'{save_name}.png')
        res_info['element_html_path'] = os.path.join(
            self.html_path, f'{save_name}.html'
        )
        logger.info('| Finish parsing index - quick navigation - element...')

        ###################################Get the element##########################################

        # Convert the element to scrapy selector
        element = Selector(text=content)

        ###################################Get sub elements#########################################
        logger.info('| Start parsing index - quick navigation - sub elements...')
        # Start get sub elements
        res_info['element_data']: List[Dict[str, Any]] = []  # type: ignore
        sub_class_name = 'div.kingkong-16-item'

        sub_elements = element.css(sub_class_name)
        for sub_element in sub_elements:
            item: Dict[str, Any] = dict()

            # Get the text of the sub element
            item['href'] = sub_element.css('a::attr(href)').get()
            item['images'] = sub_element.css('img::attr(data-src)').getall()

            res_info['element_data'].append(item)

        logger.info('| Finish parsing index - quick navigation - sub elements...')
        ###################################Get sub elements#########################################

        return res_info
