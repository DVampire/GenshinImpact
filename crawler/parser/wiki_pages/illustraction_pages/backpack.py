from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.url import add_url

__all__ = [
    'BackpackParser',
]


class BackpackParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'backpack',
        name: str = 'backpack',
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

        # Locate the matching element
        element = context_page.locator(
            'table.obc-tmpl-part.obc-tmpl-materialBaseInfo'
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

        tbody = Selector(text=content).xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        icon_url = trs[0].xpath('.//td[1]//img/@src').get().strip()
        item_info['icon_url'] = icon_url

        # 名称
        name = (
            trs[0]
            .xpath('.//td[2]//div[@class="material-td-vertical-top"]/div/text()')
            .get()
            .strip()
        )
        item_info['名称'] = name

        for tr in trs[1:]:
            label = tr.xpath('.//td[1]//label/text()').get().strip().replace('：', '')
            if label == '星级':
                value = len(tr.xpath('.//td[1]//i'))
                item_info[label] = value
            else:
                value_tag = tr.xpath(
                    './/td[1]//div[contains(@class, "material-value-wrap-full") or contains(@class, "material-value-wrap")]'
                )
                if value_tag.xpath('.//span'):
                    content = ''.join(value_tag.xpath('.//text()').getall()).strip()

                    entry_tag = value_tag.xpath(
                        './/span[@class="custom-entry-wrapper"]'
                    )
                    icon_url = entry_tag.xpath('./@data-entry-img').get().strip()
                    name = entry_tag.xpath('./@data-entry-name').get().strip()
                    url = add_url(entry_tag.xpath('./@data-entry-url').get().strip())

                    item_info[label] = {
                        'content': content,
                        'icon_url': icon_url,
                        'name': name,
                        'url': url,
                    }
                else:
                    value = '\n'.join(value_tag.xpath('.//text()').getall()).strip()
                    item_info[label] = value

        res_info['data']['基础信息'] = item_info

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
