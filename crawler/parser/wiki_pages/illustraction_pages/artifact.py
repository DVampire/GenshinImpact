from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.parse_utils import get_item
from crawler.utils.url import add_url

__all__ = [
    'ArtifactParser',
]


class ArtifactParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'artifact',
        name: str = 'artifact',
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
        save_name = f'{self.save_id:04d}_基础信息'
        self.save_id += 1

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-richBaseInfo').first  # type: ignore

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
        element = Selector(text=content)

        item_info: Dict[str, Any] = dict()  # type: ignore

        tbody = element.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        for tr in trs:
            tds = tr.xpath('.//td')

            key = get_item(tds[0])
            value = get_item(tds[1])
            item_info[str(key)] = value

        res_info['data']['基础信息'] = item_info

        logger.info('| Finish parsing page - 基础信息 - element...')

        return res_info

    async def _parse_suits_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 套装信息 - element...')
        save_name = f'{self.save_id:04d}_套装信息'
        self.save_id += 1

        # Locate the matching element
        elements = await context_page.locator(
            'table.obc-tmpl-part.obc-tmpl-artifactListV2'
        ).all()

        for element in elements:
            content, img_path, html_path = await save_element_overleaf(
                page=context_page,
                element=element,
                save_name=save_name,
                img_path=self.img_path,
                html_path=self.html_path,
                set_width_scale=self.config.set_width_scale,
                set_height_scale=self.config.set_height_scale,
            )

            # Convert the element to scrapy selector
            element = Selector(text=content)

            trs = element.xpath('.//tr')

            icon_url = trs[0].xpath('.//td[1]/img/@src').get().strip()
            name = trs[0].xpath('.//td[2]/label/text()').get().strip().replace('：', '')
            min_desc = trs[0].xpath('.//td[2]/span/text()').get().strip()
            desc = ''.join(trs[1].xpath('.//td[1]//text()').getall()).strip()
            story = ''.join(
                trs[2].xpath('.//div[@class="obc-tmpl-relic__story"]//text()').getall()
            ).strip()

            title = name
            res_info[title]: Dict[str, Any] = dict()
            res_info[title]['img_path'] = img_path
            res_info[title]['html_path'] = html_path
            res_info[title]['data']: Dict[str, Any] = dict()  # type: ignore

            item_info: Dict[str, Any] = dict()
            item_info['icon_url'] = icon_url
            item_info['name'] = name
            item_info['副名'] = min_desc
            item_info['描述'] = desc
            item_info['故事'] = story

            res_info[title]['data']['套装信息'] = item_info

        return res_info

    async def _parse_matching_recommendation(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 搭配推荐 - element...')
        save_name = f'{self.save_id:04d}_搭配推荐'
        self.save_id += 1

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-multiTable').first

        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=1.0,
            set_height_scale=4.0,
        )

        # Save the results to the dictionary
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()  # type: ignore

        selector = Selector(text=content)

        tbody = selector.xpath('.//tbody')[0]

        trs = tbody.xpath('.//tr')

        item_info: Dict[str, Any] = dict()

        for tr in trs:
            tds = tr.xpath('.//td')

            td = tds[0].xpath('.//span[@class="custom-entry-wrapper"]')
            character_name = td.xpath('@data-entry-name').get().strip()
            character_icon_url = td.xpath('@data-entry-img').get().strip()
            character_url = add_url(td.xpath('@data-entry-link').get().strip())

            reason = tds[1].xpath('.//p/text()').get().strip()
            affix_matching = '\n'.join(tds[2].xpath('.//p//text()').getall()).strip()

            item_info[character_name] = {
                'name': character_name,
                'icon_url': character_icon_url,
                'url': character_url,
                '推荐原因': reason,
                '词缀搭配': affix_matching,
            }

        res_info['data']['角色推荐'] = item_info

        logger.info('| Finish parsing page - 搭配推荐 - element...')

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

        suits_info = await self._parse_suits_info(context_page, browser_context)
        res_info.update(suits_info)

        res_info['搭配推荐'] = await self._parse_matching_recommendation(
            context_page, browser_context
        )

        return res_info
