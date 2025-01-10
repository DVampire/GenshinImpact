import asyncio
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.url import add_url

__all__ = [
    'StrategyParser',
]


class StrategyParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'strategy',
        name: str = 'strategy',
        **kwargs,
    ) -> None:
        # Initialize the parent class
        super().__init__(
            config=config,
            url=url,
            id=id,
            name=name,
            img_path=img_path,
            html_path=html_path,
        )

    async def _parse_quick_navigation(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 快捷导航 - element...')

        save_name = f'{self.save_id:04d}_快捷导航'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(0)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=self.config.set_width_scale,
            set_height_scale=self.config.set_height_scale,
        )

        # Save the results to the dictionary
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()  # type: ignore

        element = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        # Start get sub elements
        sub_elements_list = element.css('div.kingkong-16-item')

        for idx, sub_element in enumerate(sub_elements_list):
            # Get the text of the sub element
            url = add_url(sub_element.css('a::attr(href)').get())
            image_urls = sub_element.css('img::attr(data-src)').getall()
            image_url1 = image_urls[0]
            image_url2 = image_urls[1]

            item_info[str(idx)] = {
                'url': url,
                'image_url1': image_url1,
                'image_url2': image_url2,
            }

        res_info['data']['快捷链接'] = item_info

        logger.info('| Finish parsing page - 快捷导航 - element...')

        return res_info

    async def _parse_explore(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 玩法探索 - element...')
        save_name = f'{self.save_id:04d}_玩法探索'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(1)
        element = element.locator('li.home__position').nth(0)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=self.config.set_width_scale,
            set_height_scale=self.config.set_height_scale,
        )

        # Save the results to the dictionary
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        logger.info('| Finish parsing page - 玩法探索 - element...')

        return res_info

    async def _parse_card_strategy(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 卡组攻略 - element...')

        save_name = f'{self.save_id:04d}_卡组攻略'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(1)
        element = element.locator('li.home__position').nth(1)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=self.config.set_width_scale,
            set_height_scale=self.config.set_height_scale,
        )

        # Save the results to the dictionary
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        logger.info('| Finish parsing page - 卡组攻略 - element...')

        return res_info

    async def _parse_video_strategy(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 视频攻略 - element...')

        save_name = f'{self.save_id:04d}_视频攻略'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(1)
        element = element.locator('li.home__position').nth(2)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=self.config.set_width_scale,
            set_height_scale=self.config.set_height_scale,
        )

        # Save the results to the dictionary
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        logger.info('| Finish parsing page - 视频攻略 - element...')

        return res_info

    async def _parse_npc_challenge(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - npc挑战 - element...')

        save_name = f'{self.save_id:04d}_npc挑战'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(1)
        element = element.locator('li.home__position').nth(3)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=self.config.set_width_scale,
            set_height_scale=self.config.set_height_scale,
        )

        # Save the results to the dictionary
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        logger.info('| Finish parsing page - npc挑战 - element...')

        return res_info

    async def _parse_fan_creation(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 同人内容 - element...')

        save_name = f'{self.save_id:04d}_同人内容'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(1)
        element = element.locator('li.home__position').nth(4)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=self.config.set_width_scale,
            set_height_scale=self.config.set_height_scale,
        )

        # Save the results to the dictionary
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        logger.info('| Finish parsing page - 同人内容 - element...')

        return res_info

    async def _parse_indexing(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 索引分类 - element...')
        save_name = f'{self.save_id:04d}_索引分类'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(1)
        element = element.locator('li.home__position').nth(5)

        # Capture a screenshot of the element
        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=self.config.set_width_scale,
            set_height_scale=self.config.set_height_scale,
        )

        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        element = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        sub_elements_list = element.css('li.position-list__item')

        for sub_element in sub_elements_list:
            url = add_url(sub_element.css('a::attr(href)').get())
            name = sub_element.css('a::attr(title)').get()
            image_url = sub_element.css('img::attr(data-src)').get()

            item_info[name] = {
                'url': url,
                'name': name,
                'image_url': image_url,
            }

        res_info['data']['索引分类'] = item_info

        logger.info('| Finish parsing page - 索引分类 - element...')

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

        # Wait for the element to load
        await context_page.wait_for_selector('ul.home__map')  # type: ignore
        await asyncio.sleep(1)

        res_info['快捷导航'] = await self._parse_quick_navigation(
            context_page, browser_context
        )

        res_info['玩法探索'] = await self._parse_explore(context_page, browser_context)

        res_info['卡组攻略'] = await self._parse_card_strategy(
            context_page, browser_context
        )

        res_info['视频攻略'] = await self._parse_video_strategy(
            context_page, browser_context
        )

        res_info['npc挑战'] = await self._parse_npc_challenge(
            context_page, browser_context
        )

        res_info['同人内容'] = await self._parse_fan_creation(
            context_page, browser_context
        )

        res_info['索引分类'] = await self._parse_indexing(context_page, browser_context)

        return res_info
