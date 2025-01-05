import os
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element
from crawler.utils.url import add_url

__all__ = [
    'StrategyParser',
]


class StrategyParser(AbstractParser):
    def __init__(self, config, url: str, page_name='strategy') -> None:
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
        await context_page.goto(self.url)  # type: ignore

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')  # type: ignore

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
        res_info = await self._parse(context_page)

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
        elements = context_page.locator(class_name)  # type: ignore

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

        ###################################Get the 玩法探索##################################################
        res_explore_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 玩法探索 - element...')
        save_name = f'{2:04d}_玩法探索'

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
        logger.info('| Finish parsing page - 玩法探索 - element...')

        # TODO: DO NOT parse the sub elements of 玩法探索 for now, as it is not necessary.

        res_info['玩法探索'] = res_explore_info
        ###################################Get the 玩法探索##################################################

        ###################################Get the 卡组攻略#####################################################
        res_cards_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 卡组攻略 - element...')
        save_name = f'{4:04d}_卡组攻略'

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

        logger.info('| Finish parsing page - 卡组攻略 - element...')
        # TODO: DO NOT parse the sub elements of 卡组攻略 for now, as it is not necessary.

        res_info['卡组攻略'] = res_cards_info
        ###################################Get the 卡组攻略#####################################################

        ###################################Get the 视频攻略#############################################
        res_video_gallery_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 视频攻略 - element...')
        save_name = f'{5:04d}_视频攻略'

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

        logger.info('| Finish parsing page - 视频攻略 - element...')
        # TODO: DO NOT parse the sub elements of 视频攻略 for now, as it is not necessary.

        res_info['视频攻略'] = res_video_gallery_info
        ################################ Get the 视频攻略#############################################

        ###################################Get the npc挑战#############################################
        res_npc_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - npc挑战 - element...')
        save_name = f'{6:04d}_npc挑战'

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

        logger.info('| Finish parsing page - npc挑战 - element...')
        # TODO: DO NOT parse the sub elements of npc挑战 for now, as it is not necessary.

        res_info['npc挑战'] = res_npc_info
        ###################################Get the npc挑战#############################################

        ###################################Get the fan 同人内容#############################################
        res_fan_creation_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 同人内容 - element...')
        save_name = f'{7:04d}_同人内容'

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

        logger.info('| Finish parsing page - 同人内容 - element...')
        # TODO: DO NOT parse the sub elements of 同人内容 for now, as it is not necessary.

        res_info['同人内容'] = res_fan_creation_info
        ###################################Get the 同人内容#############################################

        ###################################Get the 索引分类################################################
        res_indexing_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 索引分类 - element...')
        save_name = f'{8:04d}_索引分类'

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

        logger.info('| Finish parsing page - 索引分类 - element...')

        # Convert the element to scrapy selector
        element = Selector(text=content)

        logger.info('| Start parsing page - 索引分类 - sub elements...')
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

        logger.info('| Finish parsing page - 索引分类 - sub elements...')

        res_info['索引分类'] = res_indexing_info

        ###################################Get the 索引分类################################################

        return res_info
