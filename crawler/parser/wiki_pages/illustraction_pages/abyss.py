import asyncio
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf, save_html_file
from crawler.utils.url import add_url

__all__ = [
    'AbyssParser',
]


class AbyssParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'abyss',
        name: str = 'abyss',
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

    async def _parse_geologic_anomaly(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 地脉异常 - element...')

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-multiTable')

        save_name = f'{self.save_id:04d}_地脉异常'
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

        res_info['data']['地脉异常'] = item_info

        logger.info('| Finish parsing page - 地脉异常 - element...')

        return res_info

    async def _parse_target(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 目标 - element...')

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-spiralAbyssTarget')

        save_name = f'{self.save_id:04d}_目标'
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

        slides = (
            await element.locator('div.mhy-swiper')
            .locator('li.swiper-pagination-bullet')
            .all()
        )
        slides_data = (
            await element.locator('div.mhy-swiper').locator('div.swiper-slide').all()
        )

        for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            item_info: Dict[str, Any] = dict()

            name = await slide.text_content()

            await slide.click()
            await asyncio.sleep(1)

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

            tbody = selector.xpath('.//tbody')

            trs = tbody.xpath('.//tr')

            # 描述
            desc = '\n'.join(trs[0].xpath('.//td[1]//text()').getall()).strip()
            item_info['描述'] = desc

            # 等级
            level = trs[1].xpath('.//td[1]//text()').get().strip()
            item_info['等级'] = level

            # 轮数
            for tr in trs[2:]:
                label = tr.xpath('.//td[1]//text()')

                if label:
                    label = label.get().strip()
                else:
                    continue

                lis = tr.xpath('.//td[2]//li')
                values = []

                for li in lis:
                    icon_url = (
                        li.xpath('.//img[@class="obc-tmpl__material-image"]/@src')
                        .get()
                        .strip()
                    )
                    url = add_url(li.xpath('.//a/@href').get().strip())
                    name = (
                        li.xpath('.//p[@class="obc-tmpl__material-name"]/text()')
                        .get()
                        .strip()
                    )
                    amount = li.xpath('.//span[@class="obc-tmpl__material-num"]/text()')

                    if amount:
                        amount = int(amount.get().strip())
                    else:
                        amount = 1

                    values.append(
                        {
                            'icon_url': icon_url,
                            'url': url,
                            'name': name,
                            'amount': amount,
                        }
                    )

                item_info[label] = values

            res_info['data'][name] = item_info

        logger.info('| Finish parsing page - 目标 - element...')

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

        res_info['地脉异常'] = await self._parse_geologic_anomaly(
            context_page=context_page, browser_context=browser_context
        )

        res_info['目标'] = await self._parse_target(
            context_page=context_page, browser_context=browser_context
        )

        return res_info
