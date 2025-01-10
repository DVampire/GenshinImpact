from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.url import add_url

__all__ = [
    'FoodParser',
]


class FoodParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'enemy',
        name: str = 'enemy',
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
        elements = await context_page.locator(
            'table.obc-tmpl-part.obc-tmpl-materialBaseInfo'
        ).all()  # type: ignore

        for element in elements:
            title = (
                await element.locator('div.material-td-vertical-top')
                .first.locator('div')
                .first.text_content()
            )

            save_name = f'{self.save_id:04d}_基础信息_{title}'
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

            res_info[title]: Dict[str, Any] = dict()
            res_info[title]['img_path'] = img_path
            res_info[title]['html_path'] = html_path
            res_info[title]['data']: Dict[str, Any] = dict()

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

            # 星级
            rarity = len(trs[1].xpath('.//i'))
            item_info['星级'] = rarity

            # 加工成料
            spans = trs[2].xpath('.//td[1]//span[@class="custom-entry-wrapper"]')
            materials = []
            for span in spans:
                material_name = span.xpath('@data-entry-name').get().strip()
                material_icon_url = span.xpath('@data-entry-img').get().strip()
                material_amount = span.xpath('@data-entry-amount').get().strip()
                material_url = add_url(span.xpath('@data-entry-link').get().strip())

                materials.append(
                    {
                        'name': material_name,
                        'icon_url': material_icon_url,
                        'amount': material_amount,
                        'url': material_url,
                    }
                )
            item_info['加工成料'] = materials

            for tr in trs[3:]:
                label = (
                    tr.xpath('.//td[1]//label/text()').get().strip().replace('：', '')
                )
                value = (
                    tr.xpath('.//td[1]//div[@class="material-value-wrap-full"]//text()')
                    .get()
                    .strip()
                )
                item_info[label] = value

            res_info[title]['data']['基础信息'] = item_info

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

        base_info = await self._parse_base_info(
            context_page=context_page,
            browser_context=browser_context,
        )
        res_info.update(base_info)

        return res_info
