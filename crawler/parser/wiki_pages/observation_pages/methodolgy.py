from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import element_exists
from crawler.utils.string import clean_and_merge
from crawler.utils.url import add_url

__all__ = [
    'MethodologyParser',
]


class MethodologyParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'methodology',
        name: str = 'methodology',
        icon: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Initialize the parent class
        super().__init__(
            config=config,
            url=url,
            id=id,
            name=name,
            icon=icon,
            img_path=img_path,
            html_path=html_path,
        )

    async def _parse_base_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 基础信息 - element...')
        # save_name = f'{self.save_id:04d}_基础信息'
        # self.save_id += 1

        # Locate the matching element
        element = context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.without-border.obc-tmpl-collapsePanel'
        ).first
        if not await element_exists(element):
            return res_info

        # TODO: 太长了，这里不存储img_path和html_path
        # content, img_path, html_path = await save_element_overleaf(
        #     page=context_page,
        #     element=element,
        #     save_name=save_name,
        #     img_path=self.img_path,
        #     html_path=self.html_path,
        #     set_width_scale=self.config.set_width_scale,
        #     set_height_scale=self.config.set_height_scale,
        # )
        content = await element.evaluate('el => el.outerHTML')

        # Save the results to the dictionary
        res_info['img_path'] = ''
        res_info['html_path'] = ''
        res_info['data']: Dict[str, Any] = dict()  # type: ignore

        # Convert the element to scrapy selector
        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()  # type: ignore

        xbox = selector.xpath('.//div[contains(@class, "obc-tmpl__paragraph-box")]')

        ps = xbox.xpath('.//p')

        values = []

        for p in ps:
            content = ''.join(p.xpath('.//text()').getall()).strip()

            url = None
            a = p.xpath('.//a')
            if a:
                url = add_url(a.xpath('./@href').get().strip())

            image_urls = []
            spans = p.xpath('.//span[@class="custom-image-wrapper"]')
            if spans:
                for span in spans:
                    img = span.xpath('.//img')
                    if img:
                        image_url = img.xpath('./@src').get().strip()
                        image_urls.append(image_url)

            if url is None and len(image_urls) == 0:
                values.append(content)
            elif url is not None and len(image_urls) > 0:
                if content.strip():
                    values.append(
                        {'url': url, 'image_urls': image_urls, 'content': content}
                    )
                else:
                    values.append({'url': url, 'image_urls': image_urls})
            elif url is not None:
                if content.strip():
                    values.append({'url': url, 'content': content})
                else:
                    values.append({'url': url})
            elif len(image_urls) > 0:
                if content.strip():
                    values.append({'image_urls': image_urls, 'content': content})
                else:
                    values.append({'image_urls': image_urls})

        values = clean_and_merge(values)

        item_info['values'] = values

        res_info['data']['基础信息'] = item_info

        logger.info('| Finish parsing page - 基础信息 - element...')

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

        return res_info
