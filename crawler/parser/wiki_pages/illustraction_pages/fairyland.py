from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf, save_html_file
from crawler.utils.url import add_url

__all__ = [
    'FairylandParser',
]


class FairylandParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'fairyland',
        name: str = 'fairyland',
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
        element = context_page.locator('table.obc-tmpl-part.obc-tmpl-caveBaseInfo')

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
        name = trs[0].xpath('.//td[2]/text()').get().strip()
        item_info['名称'] = name

        # 星级
        rarity = len(trs[1].xpath('.//i'))
        item_info['星级'] = rarity

        # 合成成料
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

        res_info['data']['基础信息'] = item_info

        logger.info('| Finish parsing page - 基础信息 - element...')

        return res_info

    async def _parse_item_description(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 物品描述 - element...')

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-goodDesc')

        save_name = f'{self.save_id:04d}_物品描述'
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

        item_info['内容'] = '\n'.join(selector.xpath('.//text()').getall()).strip()

        res_info['data']['物品描述'] = item_info

        logger.info('| Finish parsing page - 物品描述 - element...')

        return res_info

    async def _parse_base_attribute(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 基础属性 - element...')

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-richBaseInfo')

        save_name = f'{self.save_id:04d}_基础属性'
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

        for tr in trs:
            key = tr.xpath('.//td[1]//text()').get().strip()
            value = tr.xpath('.//td[2]//text()').get().strip()

            item_info[key] = value

        res_info['data']['基础属性'] = item_info

        logger.info('| Finish parsing page - 基础属性 - element...')

        return res_info

    async def _parse_map_text(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 地图说明 - element...')

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-mapDesc')

        save_name = f'{self.save_id:04d}_地图说明'
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

        slides = ['地图说明']
        slides_data = (
            await element.locator('div.mhy-swiper').locator('div.swiper-slide').all()
        )

        for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            item_info: Dict[str, Any] = dict()

            name = slide

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

            content = await slide_data.inner_html()

            # Overwrite the HTML content to a file
            save_html_file(content, html_path)

            item_info['img_path'] = img_path
            item_info['html_path'] = html_path

            selector = Selector(text=content)

            image_url = selector.xpath('.//source/@srcset').get().strip()
            item_info['image_url'] = image_url

            res_info['data'][name] = item_info

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

        res_info['物品描述'] = await self._parse_item_description(
            context_page=context_page, browser_context=browser_context
        )

        res_info['基础属性'] = await self._parse_base_attribute(
            context_page=context_page, browser_context=browser_context
        )

        res_info['地图说明'] = await self._parse_map_text(
            context_page=context_page, browser_context=browser_context
        )

        return res_info
