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
    'WikiParser',
]


class WikiParser(AbstractParser):
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
        await page.wait_for_selector('div[class="calendar"]')

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

        class_name = 'ul.home__map'
        # Wait for the element to load
        await page.wait_for_selector(class_name)  # type: ignore
        # Locate the matching elements
        elements = page.locator(class_name)

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

        ###################################Get the calendar##################################################
        res_calendar_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - calendar - element...')
        save_name = f'{2:04d}_calendar'

        element = elements.nth(1)  # the second element

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_calendar_info['element_img_path'] = img_path
        res_calendar_info['element_html_path'] = html_path
        res_calendar_info['element_data']: List[Dict[str, Any]] = []  # type: ignore
        logger.info('| Finish parsing page - calendar - element...')

        # TODO: DO NOT parse the sub elements of calendar for now, as it is not necessary.

        res_info['calendar'] = res_calendar_info
        ###################################Get the calendar##################################################

        ###################################Get the illustration##############################################
        res_illustration_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - illustration - element...')
        save_name = f'{3:04d}_illustration'

        element = elements.nth(2)  # the third element

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_illustration_info['element_img_path'] = img_path
        res_illustration_info['element_html_path'] = html_path
        res_illustration_info['element_data']: List[Dict[str, Any]] = []  # type: ignore

        logger.info('| Finish parsing page - illustration - element...')

        # TODO: DO NOT parse the sub elements of illustration for now, as it is not necessary.

        res_info['illustration'] = res_illustration_info
        ###################################Get the illustration##############################################

        ###################################Get the cards#####################################################
        res_cards_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - cards - element...')
        save_name = f'{4:04d}_cards'

        element = elements.nth(3)  # the fourth element
        element = element.locator('li.home__position').nth(0)

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

        element = elements.nth(3)  # the fourth element
        element = element.locator('li.home__position').nth(1)

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

        ###################################Get the observation#############################################
        res_observation_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - observation - element...')
        save_name = f'{6:04d}_observation'

        element = elements.nth(3)  # the fourth element
        element = element.locator('li.home__position').nth(2)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        res_observation_info['element_img_path'] = img_path
        res_observation_info['element_html_path'] = html_path
        res_observation_info['element_data']: List[Dict[str, Any]] = []

        logger.info('| Finish parsing page - observation - element...')
        # TODO: DO NOT parse the sub elements of observation for now, as it is not necessary.

        res_info['observation'] = res_observation_info
        ###################################Get the observation#############################################

        ###################################Get the indexing################################################
        res_indexing_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - indexing - element...')
        save_name = f'{7:04d}_indexing'

        element = elements.nth(3)  # the fourth element
        element = element.locator('li.home__position').nth(3)

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
