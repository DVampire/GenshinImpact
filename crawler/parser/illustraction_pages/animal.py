from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.url import add_url

__all__ = [
    'AnimalParser',
]


class AnimalParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'animal',
        name: str = 'animal',
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

    async def _parse_base_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 基础信息 - element...')

        # Locate the matching element
        element = context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-monsterBaseInfo'
        ).first

        save_name = f'{self.save_id:04d}_基础信息'
        self.save_id += 1

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

        item_info: Dict[str, Any] = dict()

        selector = Selector(text=content)

        # span.custom-image-view
        image_url = selector.xpath('.//source/@srcset').extract_first()

        item_info['image_url'] = image_url
        item_info['name'] = self.name

        tbody = selector.xpath('.//tbody')
        trs = tbody.xpath('.//tr')

        for tr in trs:
            label = tr.xpath('./td[1]/text()').get().strip()
            value = tr.xpath('./td[2]//text()').get().strip()
            item_info[label] = value

        res_info['data']['基础信息'] = item_info

        return res_info

    async def _parse_background_story(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 背景故事 - element...')

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-goodDesc').first

        save_name = f'{self.save_id:04d}_背景故事'
        self.save_id += 1

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

        item_info: Dict[str, Any] = dict()

        selector = Selector(text=content)

        item_info['内容'] = '\n'.join(
            selector.xpath('.//tbody//text()').getall()
        ).strip()

        res_info['data']['背景故事'] = item_info

        return res_info

    async def _parse_strategy(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 攻略方法 - element...')

        # Locate the matching element
        elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()

        # filter the element
        element = None
        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').text_content()
            if '攻略方法' in title:
                element = ele
                break

        save_name = f'{self.save_id:04d}_攻略方法'
        self.save_id += 1

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

        item_info: Dict[str, Any] = dict()

        selector = Selector(text=content)

        xbox = selector.xpath('.//div[@class="obc-tmpl__paragraph-box  "]')

        content = ''.join(xbox.xpath('.//text()').getall()).strip()
        span = xbox.xpath('.//span[@class="custom-entry-wrapper"]')
        if span:
            entry_img_url = span.xpath('@data-entry-img').get().strip()
            entry_name = span.xpath('@data-entry-name').get().strip()
            entry_url = add_url(span.xpath('@data-entry-link').get().strip())
            item_info['image_url'] = entry_img_url
            item_info['name'] = entry_name
            item_info['url'] = entry_url
        item_info['content'] = content

        res_info['data']['攻略方法'] = item_info

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

        res_info['基础信息'] = await self._parse_base_info(
            context_page=context_page, browser_context=browser_context
        )

        res_info['背景故事'] = await self._parse_background_story(
            context_page=context_page, browser_context=browser_context
        )

        res_info['攻略方法'] = await self._parse_strategy(
            context_page=context_page, browser_context=browser_context
        )

        return res_info
