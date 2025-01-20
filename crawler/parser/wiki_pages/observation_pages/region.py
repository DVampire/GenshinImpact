from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import element_exists, save_element_overleaf, save_html_file
from crawler.utils.url import add_url

__all__ = [
    'RegionParser',
]


class RegionParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'region',
        name: str = 'region',
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
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-baseInfo').first
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

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')
        for tr in trs:
            key = tr.xpath('./td[1]//text()').get().strip()
            value = tr.xpath('./td[2]//text()').get().strip()
            item_info[key] = value

        res_info['data']['基础信息'] = item_info

        logger.info('| Finish parsing page - 基础信息 - element...')

        return res_info

    async def _parse_series_task(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 系列任务 - element...')
        save_name = f'{self.save_id:04d}_系列任务'
        self.save_id += 1

        # Locate the matching element
        elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-richBaseInfo'
        ).all()

        if not await element_exists(elements):
            return res_info

        element = None
        for ele in elements:
            title = await ele.locator('h2.wiki-h2').text_content()
            if '系列任务' in title:
                element = ele
                break

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
        res_info['data']: Dict[str, Any] = dict()

        # Convert the element to scrapy selector
        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        for tr in trs:
            key = tr.xpath('./td[1]//text()').get().strip()

            value = tr.xpath('./td[2]')

            content = '\n'.join(value.xpath('.//text()').getall()).strip()
            spans = value.xpath('.//span[@class="custom-entry-wrapper"]')

            value_list = []
            if spans:
                for span in spans:
                    image_url = span.xpath('./@data-entry-img').get().strip()
                    name = span.xpath('./@data-entry-name').get().strip()
                    url = add_url(span.xpath('./@data-entry-link').get().strip())

                    value_list.append(
                        {
                            'image_url': image_url,
                            'name': name,
                            'url': url,
                        }
                    )

                item_info[key] = {
                    'content': content,
                    'values': value_list,
                }
            else:
                item_info[key] = content

        res_info['data']['系列任务'] = item_info

        logger.info('| Finish parsing page - 系列任务 - element...')

        return res_info

    async def _parse_map_text(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 描述 - element...')

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-mapDesc')

        save_name = f'{self.save_id:04d}_描述'
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

        slides = ['描述']
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

    async def _parse_monster_distribution(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 怪物分布 - element...')

        # Locate the matching element
        elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-richBaseInfo'
        ).all()
        element = None
        for ele in elements:
            title = await ele.locator('h2.wiki-h2').text_content()
            if '怪物分布' in title:
                element = ele
                break

        save_name = f'{self.save_id:04d}_怪物分布'
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

        # Convert the element to scrapy selector
        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        for tr in trs:
            key = tr.xpath('./td[1]//text()').get().strip()
            value = tr.xpath('./td[2]')

            spans = value.xpath('.//span[@class="custom-entry-wrapper"]')

            if spans:
                values = []
                for span in spans:
                    image_url = span.xpath('./@data-entry-img').get().strip()
                    name = span.xpath('./@data-entry-name').get().strip()
                    url = add_url(span.xpath('./@data-entry-link').get().strip())

                    values.append(
                        {
                            'image_url': image_url,
                            'name': name,
                            'url': url,
                        }
                    )

                item_info[key] = values
            else:
                item_info[key] = ''.join(value.xpath('.//text()').getall()).strip()

        res_info['data']['怪物分布'] = item_info

        logger.info('| Finish parsing page - 怪物分布 - element...')

        return res_info

    async def _parse_trap(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 机关 - element...')

        # Locate the matching element
        elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-richBaseInfo'
        ).all()
        element = None
        for ele in elements:
            title = await ele.locator('h2.wiki-h2').text_content()
            if '机关' in title:
                element = ele
                break

        save_name = f'{self.save_id:04d}_机关'
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

        # Convert the element to scrapy selector
        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        for tr in trs:
            key = tr.xpath('./td[1]//text()').get().strip()
            value = tr.xpath('./td[2]')

            content = '\n'.join(value.xpath('.//text()').getall()).strip()
            spans = value.xpath('.//span[@class="custom-entry-wrapper"]')

            value_list = []
            if spans:
                for span in spans:
                    image_url = span.xpath('./@data-entry-img').get().strip()
                    name = span.xpath('./@data-entry-name').get().strip()
                    url = add_url(span.xpath('./@data-entry-link').get().strip())

                    value_list.append(
                        {
                            'image_url': image_url,
                            'name': name,
                            'url': url,
                        }
                    )

                item_info[key] = {
                    'content': content,
                    'values': value_list,
                }
            else:
                item_info[key] = content

        res_info['data']['机关'] = item_info

        logger.info('| Finish parsing page - 机关 - element...')

        return res_info

    async def _parse_map_resource(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 地图资源 - element...')

        # Locate the matching element
        elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-richBaseInfo'
        ).all()
        element = None
        for ele in elements:
            title = await ele.locator('h2.wiki-h2').text_content()
            if '地图资源' in title:
                element = ele
                break

        save_name = f'{self.save_id:04d}_地图资源'
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

        # Convert the element to scrapy selector
        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        for tr in trs:
            key = tr.xpath('./td[1]//text()').get().strip()
            value = tr.xpath('./td[2]')

            content = '\n'.join(value.xpath('.//text()').getall()).strip()
            spans = value.xpath('.//span[@class="custom-entry-wrapper"]')

            value_list = []
            if spans:
                for span in spans:
                    image_url = span.xpath('./@data-entry-img').get().strip()
                    name = span.xpath('./@data-entry-name').get().strip()
                    url = add_url(span.xpath('./@data-entry-link').get().strip())

                    value_list.append(
                        {
                            'image_url': image_url,
                            'name': name,
                            'url': url,
                        }
                    )

                item_info[key] = {
                    'content': content,
                    'values': value_list,
                }
            else:
                item_info[key] = content

        res_info['data']['地图资源'] = item_info

        logger.info('| Finish parsing page - 地图资源 - element...')

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

        res_info['系列任务'] = await self._parse_series_task(
            context_page=context_page, browser_context=browser_context
        )

        res_info['描述'] = await self._parse_map_text(
            context_page=context_page, browser_context=browser_context
        )

        res_info['怪物分布'] = await self._parse_monster_distribution(
            context_page=context_page, browser_context=browser_context
        )

        res_info['机关'] = await self._parse_trap(
            context_page=context_page, browser_context=browser_context
        )

        res_info['地图资源'] = await self._parse_map_resource(
            context_page=context_page, browser_context=browser_context
        )

        return res_info
