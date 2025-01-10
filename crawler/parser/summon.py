from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.url import add_url

__all__ = [
    'SummonParser',
]


class SummonParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'summon',
        name: str = 'summon',
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

        elements = context_page.locator('div.summon-content')
        element = elements.nth(0)
        element = element.locator('div.summon-king').nth(0)

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
        sub_elements_list = element.css('div.summon-king__list')
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

    async def _parse_card_strategy(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 卡组攻略 - element...')

        save_name = f'{self.save_id:04d}_卡组攻略'
        self.save_id += 1

        elements = context_page.locator('div.home__position')
        element = elements.nth(0)
        element = element.locator('div.home-channel').nth(0)

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

    async def _parse_npc_challenge(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - npc挑战 - element...')

        save_name = f'{self.save_id:04d}_npc挑战'
        self.save_id += 1

        elements = context_page.locator('div.home__position')
        element = elements.nth(0)
        element = element.locator('div.home-channel').nth(1)

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

    async def _parse_video_gallery(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 视频攻略 - element...')

        save_name = f'{self.save_id:04d}_视频攻略'
        self.save_id += 1

        elements = context_page.locator('div.home__position')
        element = elements.nth(0)
        element = element.locator('div.home-channel').nth(2)

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
        await context_page.wait_for_selector('div.summon-content')  # type: ignore
        await context_page.wait_for_selector('div.home__position')  # type: ignore

        res_info['快捷导航'] = await self._parse_quick_navigation(
            context_page, browser_context
        )

        res_info['卡组攻略'] = await self._parse_card_strategy(
            context_page, browser_context
        )

        res_info['npc挑战'] = await self._parse_npc_challenge(
            context_page, browser_context
        )

        res_info['视频攻略'] = await self._parse_video_gallery(
            context_page, browser_context
        )

        return res_info
