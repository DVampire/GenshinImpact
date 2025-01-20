import asyncio
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.html_files import save_html_file
from crawler.utils.url import add_url

__all__ = [
    'WeaponParser',
]


class WeaponParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'weapon',
        name: str = 'weapon',
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
            'table.obc-tmpl-part.obc-tmpl-equipmentBaseInfo'
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

        # Convert the element to scrapy selector
        element = Selector(text=content)

        item_info: Dict[str, Any] = dict()  # type: ignore

        tbody = element.xpath('.//tbody')

        item_info['icon_url'] = tbody.xpath('.//tr[1]/td[1]/img/@src').get().strip()
        item_info['名字'] = (
            tbody.xpath('.//tr[1]/td[2]')
            .xpath('string(.)')
            .get()
            .strip()
            .replace('\n', '')
        )
        item_info['装备类型'] = (
            tbody.xpath('.//tr[2]/td[1]')
            .xpath('string(.)')
            .get()
            .strip()
            .replace('\n', '')
        )
        item_info['星级'] = len(tbody.xpath('.//tr[3]/td[1]/i').extract())

        res_info['data']['基础信息'] = item_info

        logger.info('| Finish parsing page - 基础信息 - element...')

        return res_info

    async def _parse_weapon_display(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 装备展示 - element...')
        save_name = f'{self.save_id:04d}_装备展示'
        self.save_id += 1

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-mapDesc').first

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

        for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            item_info: Dict[str, Any] = dict()

            await slide.click()
            await asyncio.sleep(1)

            save_name = f'{self.save_id:04d}_装备展示_{idx}'
            self.save_id += 1

            element = context_page.locator('div.obc-tmpl-part.obc-tmpl-mapDesc').first

            _, img_path, html_path = await save_element_overleaf(
                page=context_page,
                element=element,
                save_name=save_name,
                img_path=self.img_path,
                html_path=self.html_path,
                set_width_scale=self.config.set_width_scale,
                set_height_scale=self.config.set_height_scale,
            )

            save_html_file(content, html_path)

            item_info['img_path'] = img_path
            item_info['html_path'] = html_path
            item_info['name'] = await slide.text_content()
            item_info['image_url'] = await slide_data.locator(
                'source'
            ).first.get_attribute('srcset')

            res_info['data'][item_info['name']] = item_info

        logger.info('| Finish parsing page - 装备展示 - element...')

        return res_info

    async def _parse_growth_info(
        self,
        context_page: Page,
        browser_context: BrowserContext,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 成长数值 - element...')
        save_name = f'{self.save_id:04d}_成长数值'
        self.save_id += 1

        # Locate the matching element
        element = context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-equipmentGrowthInfo'
        ).first

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

        for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            item_info: Dict[str, Any] = dict()

            level = await slide.text_content()
            item_info['等级'] = level

            save_name = f'{self.save_id:04d}_成长数值_{level}'
            self.save_id += 1

            await slide.click()
            await asyncio.sleep(1)

            element = context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-equipmentGrowthInfo'
            ).first

            # Capture a screenshot of the element
            _, img_path, html_path = await save_element_overleaf(
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

            tbodys = selector.xpath('.//tbody')

            tbody = tbodys[0]
            item_info['初始基础数值'] = (
                tbody.xpath('.//tr[1]/td[1]//p').xpath('string(.)').get().strip()
            )
            item_info['平均每级提升'] = (
                tbody.xpath('.//tr[1]/td[2]//p').xpath('string(.)').get().strip()
            )

            if len(tbodys) == 2:
                tbody = tbodys[1]

                materials_list = tbody.xpath('.//td')

                materials = []

                for material in materials_list[1:]:
                    if not material.xpath('./*'):
                        continue

                    url = add_url(material.xpath('.//a/@href').get())
                    icon_url = material.xpath('.//img/@src').get()
                    name = (
                        material.xpath('.//span[@class="obc-tmpl__icon-text"]/text()')
                        .get()
                        .strip()
                    )
                    amount = (
                        material.xpath('.//span[@class="obc-tmpl__icon-num"]/text()')
                        .get()
                        .strip()
                        .replace('*', '')
                    )

                    materials.append(
                        {
                            'icon_url': icon_url,
                            'url': url,
                            'name': name,
                            'amount': amount,
                        }
                    )

                item_info['突破材料'] = materials

            res_info['data'][level] = item_info

        logger.info('| Finish parsing page - 成长数值 - element...')

        return res_info

    async def _parse_weapon_extend_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 武器扩展 - element...')

        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()

        for element in elements:
            title = await element.locator(
                'div.obc-tmpl-fold__title'
            ).first.text_content()

            button = None
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

            if button:
                save_name = f'{self.save_id:04d}_{title}'
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
                res_info[title]['data']: Dict[str, Any] = dict()  # type: ignore

                selector = Selector(text=content)

                item_info: Dict[str, Any] = dict()

                item_info['description'] = ''.join(
                    selector.xpath('.//p').xpath('string(.)').getall()
                ).strip()
                res_info[title]['data']['内容'] = item_info

        logger.info('| Finish parsing page - 武器扩展 - element...')
        return res_info

    async def _parse_good_description(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 装备描述 - element...')
        save_name = f'{self.save_id:04d}_装备描述'

        # Locate the matching element
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

        # Save the results to the dictionary
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()  # type: ignore

        item_info: Dict[str, Any] = dict()  # type: ignore

        selector = Selector(text=content)

        tbody = selector.xpath('.//tbody')

        item_info['精炼(1/2/3/4/5)阶'] = ''.join(
            tbody.xpath('.//tr[1]/td[1]//p').xpath('string(.)').getall()
        ).strip()
        item_info['冒险等级限制'] = ''.join(
            tbody.xpath('.//tr[2]/td[1]//p').xpath('string(.)').getall()
        ).strip()
        item_info['获取途径'] = ''.join(
            tbody.xpath('.//tr[3]/td[1]//p').xpath('string(.)').getall()
        ).strip()

        res_info['data']['装备描述'] = item_info

        logger.info('| Finish parsing page - 装备描述 - sub elements...')

        return res_info

    async def _parse_recommand_character_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 推荐角色 - element...')
        save_name = f'{self.save_id:04d}_推荐角色'
        self.save_id += 1

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-multiTable').first

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

        item_info: Dict[str, Any] = dict()

        selector = Selector(text=content)

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        for tr in trs:
            tds = tr.xpath('.//td')

            td = tds[0].xpath('.//span[@class="custom-entry-wrapper"]')
            if td:
                icon_url = td.xpath('@data-entry-img').get().strip()
                name = td.xpath('@data-entry-name').get().strip()
                url = add_url(td.xpath('@data-entry-link').get().strip())
                description = tds[1].xpath('string(.)').get().strip()

                item_info[name] = {
                    'icon_url': icon_url,
                    'name': name,
                    'url': url,
                    'description': description,
                }

            else:
                name = tds[0].xpath('string(.)').get().strip()
                description = tds[1].xpath('string(.)').get().strip()
                item_info[name] = {
                    'name': name,
                    'description': description,
                }

        res_info['data']['推荐角色'] = item_info

        logger.info('| Finish parsing page - 推荐角色 - sub elements...')

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

        res_info['装备展示'] = await self._parse_weapon_display(
            context_page, browser_context
        )

        res_info['成长数值'] = await self._parse_growth_info(
            context_page, browser_context
        )

        res_info['装备描述'] = await self._parse_good_description(
            context_page, browser_context
        )

        weapon_extend_info = await self._parse_weapon_extend_info(
            context_page, browser_context
        )
        res_info.update(weapon_extend_info)

        res_info['推荐角色'] = await self._parse_recommand_character_info(
            context_page, browser_context
        )

        return res_info
