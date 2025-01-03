import os
from typing import Any, Dict, List, Optional

from playwright.async_api import Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element
from crawler.utils.html_files import save_html_file
from crawler.utils.screenshot import scroll_and_capture

__all__ = [
    'StrategyParser',
]


class StrategyParser(AbstractParser):
    def __init__(self, config, url: str, page_name='strategy') -> None:
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
        await page.goto(self.url)  # type: ignore

        # Ensure all network activity is complete
        await page.wait_for_load_state('networkidle')  # type: ignore

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
        await scroll_and_capture(
            page, os.path.join(self.img_path, f'{save_name}.png'), sleep_time=3
        )

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

        class_name = 'ul.home__map'
        # Wait for the element to load
        await page.wait_for_selector(class_name)  # type: ignore
        # Locate the matching elements
        elements = page.locator(class_name)  # type: ignore

        ###################################Get the quick navigation##########################################
        res_quick_navigation_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - quick navigation - element...')
        save_name = f'{1:04d}_quick_navigation'

        element = elements.nth(0)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        # Save the results to the dictionary
        res_quick_navigation_info['element_img_path'] = img_path
        res_quick_navigation_info['element_html_path'] = html_path
        logger.info('| Finish parsing page - quick navigation - element...')

        # Convert the element to scrapy selector
        element = Selector(text=content)

        logger.info('| Start parsing page - quick navigation - sub elements...')
        # Start get sub elements
        res_quick_navigation_info['element_data']: List[Dict[str, Any]] = []  # type: ignore
        sub_class_name = 'div.kingkong-16-item'

        sub_elements = element.css(sub_class_name)
        for sub_element in sub_elements:
            item: Dict[str, Any] = dict()

            # Get the text of the sub element
            item['href'] = sub_element.css('a::attr(href)').get()
            item['images'] = sub_element.css('img::attr(data-src)').getall()

            res_quick_navigation_info['element_data'].append(item)

        logger.info('| Finish parsing page - quick navigation - sub elements...')

        res_info['quick_navigation'] = res_quick_navigation_info
        ###################################Get the quick navigation##########################################

        ###################################Get the explore##################################################
        res_explore_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - explore - element...')
        save_name = f'{2:04d}_explore'

        element = elements.nth(1)
        element = element.locator('li.home__position').nth(0)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_explore_info['element_img_path'] = img_path
        res_explore_info['element_html_path'] = html_path
        res_explore_info['element_data']: List[Dict[str, Any]] = []  # type: ignore
        logger.info('| Finish parsing page - explore - element...')

        # TODO: DO NOT parse the sub elements of explore for now, as it is not necessary.

        res_info['explore'] = res_explore_info
        ###################################Get the explore##################################################

        ###################################Get the cards#####################################################
        res_cards_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - cards - element...')
        save_name = f'{4:04d}_cards'

        element = elements.nth(1)
        element = element.locator('li.home__position').nth(1)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_cards_info['element_img_path'] = img_path
        res_cards_info['element_html_path'] = html_path
        res_cards_info['element_data']: List[Dict[str, Any]] = []

        logger.info('| Finish parsing page - cards - element...')
        # TODO: DO NOT parse the sub elements of cards for now, as it is not necessary.

        res_info['cards'] = res_cards_info
        ###################################Get the cards#####################################################

        ###################################Get the video gallery#############################################
        res_video_gallery_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - video gallery - element...')
        save_name = f'{5:04d}_video_gallery'

        element = elements.nth(1)
        element = element.locator('li.home__position').nth(2)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_video_gallery_info['element_img_path'] = img_path
        res_video_gallery_info['element_html_path'] = html_path
        res_video_gallery_info['element_data']: List[Dict[str, Any]] = []

        logger.info('| Finish parsing page - video gallery - element...')
        # TODO: DO NOT parse the sub elements of video gallery for now, as it is not necessary.

        res_info['video_gallery'] = res_video_gallery_info
        ################################ Get the video gallery#############################################

        ###################################Get the npc#############################################
        res_npc_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - npc - element...')
        save_name = f'{6:04d}_npc'

        element = elements.nth(1)
        element = element.locator('li.home__position').nth(3)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_npc_info['element_img_path'] = img_path
        res_npc_info['element_html_path'] = html_path
        res_npc_info['element_data']: List[Dict[str, Any]] = []

        logger.info('| Finish parsing page - npc - element...')
        # TODO: DO NOT parse the sub elements of npc for now, as it is not necessary.

        res_info['npc'] = res_npc_info
        ###################################Get the npc#############################################

        ###################################Get the fan creation#############################################
        res_fan_creation_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - fan_creation - element...')
        save_name = f'{7:04d}_fan_creation'

        element = elements.nth(1)
        element = element.locator('li.home__position').nth(4)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_fan_creation_info['element_img_path'] = img_path
        res_fan_creation_info['element_html_path'] = html_path
        res_fan_creation_info['element_data']: List[Dict[str, Any]] = []

        logger.info('| Finish parsing page - fan_creation - element...')
        # TODO: DO NOT parse the sub elements of fan_creation for now, as it is not necessary.

        res_info['fan_creation'] = res_fan_creation_info
        ###################################Get the fan_creation#############################################

        ###################################Get the indexing################################################
        res_indexing_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - indexing - element...')
        save_name = f'{8:04d}_indexing'

        element = elements.nth(1)
        element = element.locator('li.home__position').nth(5)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_indexing_info['element_img_path'] = img_path
        res_indexing_info['element_html_path'] = html_path
        res_indexing_info['element_data']: List[Dict[str, Any]] = []

        logger.info('| Finish parsing page - indexing - element...')

        # Convert the element to scrapy selector
        element = Selector(text=content)

        logger.info('| Start parsing page - indexing - sub elements...')
        # Start get sub elements
        sub_class_name = 'li.position-list__item'
        sub_elements = element.css(sub_class_name)

        for sub_element in sub_elements:
            item: Dict[str, Any] = dict()

            # Get the text of the sub element
            item['href'] = sub_element.css('a::attr(href)').get()
            item['title'] = sub_element.css('a::attr(title)').get()
            item['images'] = sub_element.css('img::attr(data-src)').getall()
            res_indexing_info['element_data'].append(item)

        logger.info('| Finish parsing page - indexing - sub elements...')

        res_info['indexing'] = res_indexing_info

        ###################################Get the indexing################################################

        return res_info
