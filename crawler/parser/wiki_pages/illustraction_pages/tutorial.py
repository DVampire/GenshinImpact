from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf

__all__ = [
    'TutorialParser',
]


class TutorialParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'tutorial',
        name: str = 'tutorial',
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

    async def _parse_text_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 文字说明 - element...')

        # Locate the matching element
        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()

        element = None
        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').text_content()
            if '文字说明' in title:
                element = ele
                break

        save_name = f'{self.save_id:04d}_文字说明'
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

        xbox = selector.xpath('.//div[contains(@class, "obc-tmpl__paragraph-box")]')
        item_info['内容'] = '\n'.join(xbox.xpath('.//text()').getall()).strip()

        res_info['data']['文字说明'] = item_info

        return res_info

    async def _parse_image_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 图片说明 - element...')

        # Locate the matching element
        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()

        element = None
        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').text_content()
            if '图片说明' in title:
                element = ele
                break

        save_name = f'{self.save_id:04d}_图片说明'
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

        xbox = selector.xpath('.//div[contains(@class, "obc-tmpl__paragraph-box")]')

        spans = xbox.xpath('.//span[@class="custom-image-view"]')
        image_urls = []
        for span in spans:
            image_urls.append(span.xpath('./@data-image-url').get().strip())
        item_info['图片'] = image_urls

        res_info['data']['图片说明'] = item_info

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

        res_info['文字说明'] = await self._parse_text_info(
            context_page=context_page, browser_context=browser_context
        )

        res_info['图片说明'] = await self._parse_image_info(
            context_page=context_page, browser_context=browser_context
        )

        return res_info
