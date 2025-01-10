import asyncio
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.url import add_url

__all__ = [
    'WikiParser',
]


class WikiParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'wiki',
        name: str = 'wiki',
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

    async def _parse_calendar(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 日历 - element...')

        save_name = f'{self.save_id:04d}_日历'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(1)

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

        logger.info('| Finish parsing page - 日历 - element...')

        return res_info

    async def _parse_illustration(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 图鉴 - element...')

        save_name = f'{self.save_id:04d}_图鉴'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(2)

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

        logger.info('| Finish parsing page - 图鉴 - element...')

        return res_info

    async def _parse_cards_info(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 卡牌图鉴 - element...')
        save_name = f'{self.save_id:04d}_卡牌图鉴'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(3)
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

        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        logger.info('| Finish parsing page - 卡牌图鉴 - element...')

        return res_info

    async def _parse_video_gallery(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 影音回廊 - element...')
        save_name = f'{self.save_id:04d}_影音回廊'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(3)
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

        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        logger.info('| Finish parsing page - 影音回廊 - element...')

        return res_info

    async def _parse_observation(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 观测 - element...')
        save_name = f'{self.save_id:04d}_观测'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(3)
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

        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        logger.info('| Finish parsing page - 观测 - element...')

        return res_info

    async def _parse_indexing(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 各类索引 - element...')
        save_name = f'{self.save_id:04d}_各类索引'
        self.save_id += 1

        element = context_page.locator('ul.home__map').nth(3)
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

        res_info['data']['各类索引'] = item_info

        logger.info('| Finish parsing page - 各类索引 - element...')

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

        res_info['日历'] = await self._parse_calendar(context_page, browser_context)

        res_info['图鉴'] = await self._parse_illustration(context_page, browser_context)

        res_info['卡牌图鉴'] = await self._parse_cards_info(
            context_page, browser_context
        )

        res_info['影音回廊'] = await self._parse_video_gallery(
            context_page, browser_context
        )

        res_info['观测'] = await self._parse_observation(context_page, browser_context)

        res_info['各类索引'] = await self._parse_indexing(context_page, browser_context)

        return res_info
