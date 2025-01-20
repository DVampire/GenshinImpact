from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import element_exists, save_element_overleaf

__all__ = [
    'OtherVideoParser',
]


class OtherVideoParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'other_video',
        name: str = 'other_video',
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
        save_name = f'{self.save_id:04d}_基础信息'
        self.save_id += 1

        # Locate the matching element
        element = context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.without-border.obc-tmpl-collapsePanel'
        ).first
        if not await element_exists(element):
            return res_info

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

        # Convert the element to scrapy selector
        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()  # type: ignore

        xbox = selector.xpath('.//div[contains(@class, "obc-tmpl__paragraph-box")]')

        spans = xbox.xpath(
            './/span[@class="wiki-editor-extension__local-video-wrapper"]'
        )

        videos = []
        for idx, span in enumerate(spans):
            video_url = span.xpath('./@data-video-url').get().strip()
            video_poster_url = span.xpath('./@data-video-poster').get().strip()
            videos.append(
                {'video_url': video_url, 'video_poster_url': video_poster_url}
            )
        item_info['videos'] = videos

        item_info['内容'] = '\n'.join(xbox.xpath('.//text()').getall()).strip()

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
            context_page, browser_context
        )

        return res_info
