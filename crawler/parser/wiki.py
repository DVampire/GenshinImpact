import os
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element
from crawler.utils.url import add_url

__all__ = [
    'WikiParser',
]


class WikiParser(AbstractParser):
    def __init__(self, config, url: str, page_name='wiki') -> None:
        self.config = config
        self.url = url
        self.page_name = page_name

    async def parse(
        self,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        parse page
        :param page:
        :return:
        """
        # New a context page
        context_page = await browser_context.new_page()

        logger.info(f'| Go to the page {self.url}')
        # Open the page
        await context_page.goto(self.url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        logger.info('| Start parsing page...')

        self.img_path = os.path.join(self.config.img_path, self.page_name)
        os.makedirs(self.img_path, exist_ok=True)
        self.html_path = os.path.join(self.config.html_path, self.page_name)
        os.makedirs(self.html_path, exist_ok=True)

        # Save a screenshot of the page
        await self._save_screenshot(
            context_page, browser_context
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

        class_name = 'ul.home__map'
        # Wait for the element to load
        await context_page.wait_for_selector(class_name)  # type: ignore
        # Locate the matching elements
        elements = context_page.locator(class_name)

        ###################################Get the 快捷导航##########################################
        res_quick_navigation_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 快捷导航 - element...')
        save_name = f'{1:04d}_快捷导航'

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
        logger.info('| Finish parsing page - 快捷导航 - element...')

        # Convert the element to scrapy selector
        element = Selector(text=content)

        logger.info('| Start parsing page - 快捷导航 - sub elements...')
        # Start get sub elements
        res_quick_navigation_info['element_data']: List[Dict[str, Any]] = []  # type: ignore
        sub_class_name = 'div.kingkong-16-item'

        sub_elements = element.css(sub_class_name)
        for sub_element in sub_elements:
            item: Dict[str, Any] = dict()

            # Get the text of the sub element
            item['href'] = add_url(sub_element.css('a::attr(href)').get())
            item['images'] = sub_element.css('img::attr(data-src)').getall()

            res_quick_navigation_info['element_data'].append(item)

        logger.info('| Finish parsing page - 快捷导航 - sub elements...')

        res_info['快捷导航'] = res_quick_navigation_info
        ###################################Get the 快捷导航##########################################

        ###################################Get the 日历##################################################
        res_calendar_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 日历 - element...')
        save_name = f'{2:04d}_日历'

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
        logger.info('| Finish parsing page - 日历 - element...')

        # TODO: DO NOT parse the sub elements of 日历 for now, as it is not necessary.

        res_info['日历'] = res_calendar_info
        ###################################Get the 日历##################################################

        ###################################Get the 图鉴##############################################
        res_illustration_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 图鉴 - element...')
        save_name = f'{3:04d}_图鉴'

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

        logger.info('| Finish parsing page - 图鉴 - element...')

        # TODO: DO NOT parse the sub elements of 图鉴 for now, as it is not necessary.

        res_info['图鉴'] = res_illustration_info
        ###################################Get the 图鉴##############################################

        ###################################Get the 卡牌图鉴#####################################################
        res_cards_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 卡牌图鉴 - element...')
        save_name = f'{4:04d}_卡牌图鉴'

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

        logger.info('| Finish parsing page - 卡牌图鉴 - element...')
        # TODO: DO NOT parse the sub elements of 卡牌图鉴 for now, as it is not necessary.

        res_info['卡牌图鉴'] = res_cards_info
        ###################################Get the 卡牌图鉴#####################################################

        ###################################Get the 影音回廊#############################################
        res_video_gallery_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 影音回廊 - element...')
        save_name = f'{5:04d}_影音回廊'

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

        logger.info('| Finish parsing page -影音回廊 - element...')
        # TODO: DO NOT parse the sub elements of 影音回廊 for now, as it is not necessary.

        res_info['影音回廊'] = res_video_gallery_info
        ################################ Get the 影音回廊#############################################

        ###################################Get the 观测#############################################
        res_observation_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 观测 - element...')
        save_name = f'{6:04d}_观测'

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

        logger.info('| Finish parsing page - 观测 - element...')
        # TODO: DO NOT parse the sub elements of 观测 for now, as it is not necessary.

        res_info['观测'] = res_observation_info
        ###################################Get the observation#############################################

        ###################################Get the 各类索引################################################
        res_indexing_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 各类索引 - element...')
        save_name = f'{7:04d}_各类索引'

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

        logger.info('| Finish parsing page - 各类索引 - element...')

        # Convert the element to scrapy selector
        element = Selector(text=content)

        logger.info('| Start parsing page - 各类索引 - sub elements...')
        # Start get sub elements
        sub_class_name = 'li.position-list__item'
        sub_elements = element.css(sub_class_name)

        for sub_element in sub_elements:
            item: Dict[str, Any] = dict()

            # Get the text of the sub element
            item['href'] = add_url(sub_element.css('a::attr(href)').get())
            item['title'] = sub_element.css('a::attr(title)').get()
            item['images'] = sub_element.css('img::attr(data-src)').getall()
            res_indexing_info['element_data'].append(item)

        logger.info('| Finish parsing page - 各类索引 - sub elements...')

        res_info['各类索引'] = res_indexing_info

        ###################################Get the 各类索引################################################

        return res_info
