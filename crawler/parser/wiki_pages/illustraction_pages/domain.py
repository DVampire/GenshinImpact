import asyncio
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf, save_html_file
from crawler.utils.url import add_url

__all__ = [
    'DomainParser',
]


class DomainParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'domain',
        name: str = 'domain',
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
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-baseInfo').first

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

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        for tr in trs:
            key = tr.xpath('./td[@class="wiki-h3"]//text()').get().strip()
            value = tr.xpath('./td[2]//text()').get().strip()
            item_info[key] = value

        res_info['data']['基础信息'] = item_info

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

            image_url = selector.xpath('.//source/@srcset').get().strip()
            item_info['image_url'] = image_url

            res_info['data'][name] = item_info

        return res_info

    async def _parse_task_process(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 任务过程 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = None
            # Locate the matching element
            elements = await context_page.locator(
                'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
            ).all()

            for ele in elements:
                title = await ele.locator('div.obc-tmpl-fold__title').text_content()
                if '任务过程' in title:
                    element = ele
                    break

            if element:
                if (
                    await element.locator(
                        'div.el-tooltip.obc-tmpl__fold-tag.show-expand.undefined'
                    ).count()
                    > 0
                ):
                    button = element.locator(
                        'div.el-tooltip.obc-tmpl__fold-tag.show-expand.undefined'
                    ).first
                    await button.click()
                    await asyncio.sleep(1)

                save_name = f'{self.save_id:04d}_任务过程'
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

                xbox = selector.xpath(
                    './/div[contains(@class, "obc-tmpl__paragraph-box")]'
                )
                item_info['内容'] = '\n'.join(xbox.xpath('.//text()').getall()).strip()

                res_info['data']['任务过程'] = item_info

                context_page.set_default_timeout(30000)
        except Exception:
            logger.info('| No element found - 任务过程 - element...')

        logger.info('| Finish parsing page - 任务过程 - element...')

        return res_info

    async def _parse_entry(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 秘境入口 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = None
            # Locate the matching element
            elements = await context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-multiTable'
            ).all()

            for ele in elements:
                # h2.wiki-h2
                title = await ele.locator('h2.wiki-h2').text_content()
                if '秘境入口' in title:
                    element = ele
                    break

            if element:
                save_name = f'{self.save_id:04d}_秘境入口'
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

                thead = selector.xpath('.//thead')
                labels = thead.xpath('.//th//text()').getall()

                tbody = selector.xpath('.//tbody')
                values = tbody.xpath('.//td')

                for label, value in zip(labels, values):
                    img = value.xpath('.//img/@src')
                    if img:
                        item_info[label] = img.get().strip()
                    else:
                        item_info[label] = value.xpath('.//text()').get().strip()

                res_info['data']['秘境入口'] = item_info

                context_page.set_default_timeout(30000)
        except Exception:
            logger.info('| No element found - 秘境入口 - element...')

        logger.info('| Finish parsing page - 秘境入口 - element...')

        return res_info

    async def _parse_reward(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 秘境奖励 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = None
            # Locate the matching element
            elements = await context_page.locator(
                'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
            ).all()

            for ele in elements:
                title = await ele.locator('div.obc-tmpl-fold__title').text_content()
                if '秘境奖励' in title:
                    element = ele
                    break

            if element:
                save_name = f'{self.save_id:04d}_秘境奖励'
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

                tbody = selector.xpath('.//tbody')

                trs = tbody.xpath('.//tr')

                for idx, tr in enumerate(trs[1:]):
                    tds = tr.xpath('.//td')

                    values = []
                    for td in tds:
                        spans = td.xpath('.//span[@class="custom-entry-wrapper"]')

                        if len(spans) > 0:
                            for span in spans:
                                print(span.get())
                                icon_url = span.xpath('./@data-entry-img').get().strip()
                                name = span.xpath('./@data-entry-name').get().strip()
                                url = add_url(
                                    span.xpath('./@data-entry-link').get().strip()
                                )
                                amount = span.xpath('./@data-entry-amount')
                                if amount:
                                    amount = amount.get().strip()
                                    values.append(
                                        {
                                            'icon_url': icon_url,
                                            'name': name,
                                            'url': url,
                                            'amount': amount,
                                        }
                                    )
                                else:
                                    values.append(
                                        {
                                            'icon_url': icon_url,
                                            'name': name,
                                            'url': url,
                                        }
                                    )
                        else:
                            content = td.xpath('.//text()')
                            if content:
                                values.append(content.get().strip())

                    item_info[str(idx)] = values

                res_info['data']['秘境奖励'] = item_info

                context_page.set_default_timeout(30000)
        except Exception as e:
            logger.info(f'| Error occurred {e} - 秘境奖励 - element...')

        logger.info('| Finish parsing page - 秘境奖励 - element...')

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

        res_info['地图说明'] = await self._parse_map_text(
            context_page=context_page, browser_context=browser_context
        )

        res_info['任务过程'] = await self._parse_task_process(
            context_page=context_page, browser_context=browser_context
        )

        res_info['秘境入口'] = await self._parse_entry(
            context_page=context_page, browser_context=browser_context
        )

        res_info['秘境奖励'] = await self._parse_reward(
            context_page=context_page, browser_context=browser_context
        )

        # TODO: 怪物详情，因表格结构不统一，暂时没有解析

        return res_info
