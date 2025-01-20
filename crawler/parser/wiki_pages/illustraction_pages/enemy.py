import asyncio
from typing import Any, Dict, List, Optional, Union

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf

__all__ = [
    'EnemyParser',
]


class EnemyParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'enemy',
        name: str = 'enemy',
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
        element = context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-monsterBaseInfo'
        ).first  # type: ignore

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

        slides = (
            await element.locator('div.mhy-swiper')
            .locator('li.swiper-pagination-bullet')
            .all()
        )
        slides_data = (
            await element.locator('div.mhy-swiper').locator('div.swiper-slide').all()
        )

        item_info: Dict[str, Any] = dict()

        for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            skill_name = await slide.text_content()

            await slide.click()
            await asyncio.sleep(1)

            selector = Selector(text=await slide_data.inner_html())

            image_url = selector.xpath('.//source/@srcset').get().strip()

            item_info[skill_name] = {
                'name': skill_name,
                'image_url': image_url,
            }

        selector = Selector(text=content)

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        for tr in trs:
            label = str(tr.xpath('./td[1]/text()').get().strip())

            value: Union[List, str] = []

            if label == '掉落物品':
                lis = tr.xpath('./td[2]//li[@class="obc-tmpl__material-item"]')
                for li in lis:
                    value.append(
                        {
                            'icon_url': li.xpath(
                                './/img[@class="obc-tmpl__material-image"]/@src'
                            )
                            .get()
                            .strip(),
                            'name': li.xpath(
                                './/p[@class="obc-tmpl__material-name"]/text()'
                            )
                            .get()
                            .strip(),
                        }
                    )
            else:
                value = '\n'.join(tr.xpath('./td[2]//p//text()').getall()).strip()

            item_info[label] = value

        logger.info('| Finish parsing page - 基础信息 - element...')

        return res_info

    async def _pase_method_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_攻略方法'
        self.save_id += 1

        logger.info('| Start parsing page - 攻略方法 - element...')

        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()
        # filter the element
        element = None
        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').first.text_content()
            if '攻略方法' in title:
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

        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()  # type: ignore

        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        item_info['内容'] = ''.join(
            selector.xpath(
                './/div[@class="obc-tmpl__paragraph-box  "]//text()'
            ).getall()
        ).strip()

        res_info['data']['攻略方法'] = item_info

        logger.info('| Finish parsing page - 攻略方法 - element...')

        return res_info

    async def _parse_background_story(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_背景故事'
        self.save_id += 1

        logger.info('| Start parsing page - 背景故事 - element...')

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-goodDesc').first

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

        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        item_info['内容'] = ''.join(selector.xpath('.//table//text()').getall()).strip()

        res_info['data']['背景故事'] = item_info

        logger.info('| Finish parsing page - 背景故事 - element...')

        return res_info

    async def _parse_data(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_数据参考'
        self.save_id += 1

        logger.info('| Start parsing page - 数据参考 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-equipmentGrowthInfo'
            ).first  # type: ignore

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
            res_info['data']: Dict[str, Any] = dict()  # type: ignore

            item_info: Dict[str, Any] = dict()

            selector = Selector(text=content)

            thead = selector.xpath('.//thead')
            tbody = selector.xpath('.//tbody')

            ths = thead.xpath('.//th')
            tds = tbody.xpath('.//td')

            for ids, (th, td) in enumerate(zip(ths, tds)):
                label = th.xpath('.//text()').get().strip()
                value = '\n'.join(td.xpath('.//text()').getall()).strip()

                item_info[label] = value

            res_info['data']['数据参考'] = item_info

            context_page.set_default_timeout(30000)

        except Exception:
            logger.info('| No element found - 数据参考 - element...')

        logger.info('| Finish parsing page - 数据参考 - element...')

        return res_info

    async def _parse_map_desc_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 立绘展示 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = context_page.locator('div.obc-tmpl-part.obc-tmpl-mapDesc').first  # type: ignore

            save_name = f'{self.save_id:04d}_立绘展示'
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

            # Save the results to the dictionary
            res_info['img_path'] = img_path
            res_info['html_path'] = html_path
            res_info['data']: Dict[str, Any] = dict()  # type: ignore

            slides = (
                await element.locator('div.mhy-swiper')
                .locator('li.swiper-pagination-bullet')
                .all()
            )

            slides_data = (
                await element.locator('div.mhy-swiper')
                .locator('div.swiper-slide')
                .all()
            )

            item_info: Dict[str, Any] = dict()

            for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
                name = await slide.text_content()

                await slide.click()
                await asyncio.sleep(1)

                selector = Selector(text=await slide_data.inner_html())

                image_url = selector.xpath('.//source/@srcset').get().strip()

                item_info[name] = {
                    'name': name,
                    'image_url': image_url,
                }

            res_info['data']['立绘展示'] = item_info

            context_page.set_default_timeout(30000)

        except Exception:
            logger.info('| No element found - 立绘展示 - element...')

        logger.info('| Finish parsing page - 立绘展示 - element...')
        return res_info

    async def _parse_location_guide(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 位置导览 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-timelineBaseInfo'
            ).first  # type: ignore

            save_name = f'{self.save_id:04d}_位置导览'
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
            res_info['data']: Dict[str, Any] = dict()  # type: ignore

            selector = Selector(text=content)

            item_info: Dict[str, Any] = dict()

            name = (
                selector.xpath('.//div[@class="timeline-content__h3"]//text()')
                .get()
                .strip()
            )
            title = (
                selector.xpath(
                    './/div[contains(@class, "timeline-content__inner--title")]//text()'
                )
                .get()
                .strip()
            )
            desc = '\n'.join(
                selector.xpath(
                    './/div[@class="timeline-content__inner--desc"]//text()'
                ).getall()
            ).strip()
            image_url = (
                selector.xpath('.//span[@class="custom-image-view"]/@data-image-url')
                .get()
                .strip()
            )

            item_info[name] = {
                'name': name,
                'title': title,
                'desc': desc,
                'image_url': image_url,
            }

            res_info['data']['位置导览'] = item_info

            context_page.set_default_timeout(30000)

        except Exception:
            logger.info('| No element found - 位置导览 - element...')

        logger.info('| Finish parsing page - 位置导览 - element...')

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

        res_info['攻略方法'] = await self._pase_method_info(
            context_page, browser_context
        )

        res_info['背景故事'] = await self._parse_background_story(
            context_page, browser_context
        )

        data_info = await self._parse_data(context_page, browser_context)
        if data_info:
            res_info['数据参考'] = data_info

        map_desc_info = await self._parse_map_desc_info(context_page, browser_context)
        if map_desc_info:
            res_info['立绘展示'] = map_desc_info

        location_guid_info = await self._parse_location_guide(
            context_page, browser_context
        )
        if location_guid_info:
            res_info['位置导览'] = location_guid_info

        return res_info
