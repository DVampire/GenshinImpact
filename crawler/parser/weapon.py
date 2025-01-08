import asyncio
import os
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element, save_element_overleaf
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
        page_name: str,
        weapon_name: str,
        icon: str,
        img_path: str,
        html_path: str,
        **kwargs,
    ) -> None:
        self.config = config
        self.url = url
        self.page_name = page_name
        self.weapon_name = weapon_name
        self.icon = icon

        self.img_path = img_path
        self.html_path = html_path

        self.save_id = 1

    async def parse(
        self,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        parse page
        :param context_page:
        :return:
        """
        # New a context page
        context_page = await browser_context.new_page()

        logger.info(f'| Go to the page {self.url}')
        # Open the page
        await context_page.goto(self.url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')
        await asyncio.sleep(1)

        logger.info('| Start parsing page...')

        self.img_path = os.path.join(self.img_path, self.page_name)
        os.makedirs(self.img_path, exist_ok=True)
        self.html_path = os.path.join(self.html_path, self.page_name)
        os.makedirs(self.html_path, exist_ok=True)

        # Save a screenshot of the page
        # await self._save_screenshot(
        #     context_page,
        #     browser_context,
        #     sleep_time=2,
        #     remove_header=True,
        #     remove_footer=True,
        #     viewport_height_adjustment=-70,
        # )  # TODO: Comment it out for now, as this method causes the page to scroll, which slows down the speed.

        # Parse the page
        res_info = await self._parse(context_page, browser_context)

        logger.info('| Finish parsing page...')

        # Close the context page
        await context_page.close()

        return res_info

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

        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        # Save the results to the dictionary
        res_info['element_img_path'] = img_path
        res_info['element_html_path'] = html_path
        logger.info('| Finish parsing page - 基础信息 - element...')

        # Convert the element to scrapy selector
        element = Selector(text=content)

        logger.info('| Start parsing page - 基础信息 - sub elements...')
        # Start get sub elements
        res_info['element_data']: List[Dict[str, Any]] = []  # type: ignore

        item: Dict[str, Any] = dict()  # type: ignore

        tbody = element.xpath('.//tbody')

        item['icon_url'] = tbody.xpath('.//tr[1]/td[1]/img/@src').get().strip()
        item['名字'] = (
            tbody.xpath('.//tr[1]/td[2]')
            .xpath('string(.)')
            .get()
            .strip()
            .replace('\n', '')
        )
        item['装备类型'] = (
            tbody.xpath('.//tr[2]/td[1]')
            .xpath('string(.)')
            .get()
            .strip()
            .replace('\n', '')
        )
        item['星级'] = len(tbody.xpath('.//tr[3]/td[1]/i').extract())

        res_info['element_data'].append(item)

        logger.info('| Finish parsing page - 基础信息 - sub elements...')

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
            set_width_scale=1.0,
            set_height_scale=3.0,
        )

        # Save the results to the dictionary
        res_info['element_img_path'] = img_path
        res_info['element_html_path'] = html_path

        slides = (
            await element.locator('div.mhy-swiper')
            .locator('li.swiper-pagination-bullet')
            .all()
        )
        slides_data = (
            await element.locator('div.mhy-swiper').locator('div.swiper-slide').all()
        )

        res_info['element_data']: List[Dict[str, Any]] = []  # type: ignore

        for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            item: Dict[str, Any] = dict()

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
                set_width_scale=1.0,
                set_height_scale=3.0,
            )

            save_html_file(content, html_path)

            item['img_path'] = img_path
            item['html_path'] = html_path
            item['name'] = await slide.text_content()
            item['image_url'] = await slide_data.locator('source').first.get_attribute(
                'srcset'
            )

            res_info['element_data'].append(item)

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
            set_width_scale=1.0,
            set_height_scale=3.0,
        )

        # Save the results to the dictionary
        res_info['element_img_path'] = img_path
        res_info['element_html_path'] = html_path
        logger.info('| Finish parsing page - 成长数值 - element...')

        logger.info('| Start parsing page - 成长数值 - sub elements...')

        res_info['element_data']: List[Dict[str, Any]] = []  # type: ignore

        slides = (
            await element.locator('div.mhy-swiper')
            .locator('li.swiper-pagination-bullet')
            .all()
        )
        slides_data = (
            await element.locator('div.mhy-swiper').locator('div.swiper-slide').all()
        )

        for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            item: Dict[str, Any] = dict()

            level = await slide.text_content()
            item['等级'] = level

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
                set_width_scale=1.0,
                set_height_scale=3.0,
            )

            content = await slide_data.inner_html()

            # Overwrite the HTML content to a file
            save_html_file(content, html_path)
            item['img_path'] = img_path
            item['html_path'] = html_path

            selector = Selector(text=content)

            tbodys = selector.xpath('.//tbody')

            tbody = tbodys[0]
            item['初始基础数值'] = (
                tbody.xpath('.//tr[1]/td[1]//p').xpath('string(.)').get().strip()
            )
            item['平均每级提升'] = (
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

                item['突破材料'] = materials

            res_info['element_data'].append(item)

        logger.info('| Finish parsing page - 成长数值 - sub elements...')

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
            logger.info(title)

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
                    set_width_scale=1.0,
                    set_height_scale=3.0,
                )

                res_info[title]: Dict[str, Any] = dict()
                res_info[title]['element_img_path'] = img_path
                res_info[title]['element_html_path'] = html_path

                selector = Selector(text=content)

                res_info[title]['element_data']: List[Dict[str, Any]] = []

                item: Dict[str, Any] = dict()

                item['description'] = ''.join(
                    selector.xpath('.//p').xpath('string(.)').getall()
                ).strip()
                res_info[title]['element_data'].append(item)

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
            set_width_scale=1.0,
            set_height_scale=3.0,
        )

        # Save the results to the dictionary
        res_info['element_img_path'] = img_path
        res_info['element_html_path'] = html_path

        logger.info('| Finish parsing page - 装备描述 - element...')

        logger.info('| Start parsing page - 装备描述 - sub elements...')

        res_info['element_data']: List[Dict[str, Any]] = []  # type: ignore

        item: Dict[str, Any] = dict()  # type: ignore

        selector = Selector(text=content)

        tbody = selector.xpath('.//tbody')

        item['精炼(1/2/3/4/5)阶'] = ''.join(
            tbody.xpath('.//tr[1]/td[1]//p').xpath('string(.)').getall()
        ).strip()
        item['冒险等级限制'] = ''.join(
            tbody.xpath('.//tr[2]/td[1]//p').xpath('string(.)').getall()
        ).strip()
        item['获取途径'] = ''.join(
            tbody.xpath('.//tr[3]/td[1]//p').xpath('string(.)').getall()
        ).strip()

        res_info['element_data'].append(item)

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
            set_width_scale=1.0,
            set_height_scale=3.0,
        )

        # Save the results to the dictionary
        res_info['element_img_path'] = img_path
        res_info['element_html_path'] = html_path

        logger.info('| Finish parsing page - 推荐角色 - element...')

        logger.info('| Start parsing page - 推荐角色 - sub elements...')

        res_info['element_data']: List[Dict[str, Any]] = []  # type: ignore

        item: Dict[str, Any] = dict()

        selector = Selector(text=content)

        tbody = selector.xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        characters = []
        for tr in trs:
            tds = tr.xpath('.//td')

            td = tds[0].xpath('.//span[@class="custom-entry-wrapper"]')
            if td:
                icon_url = td.xpath('@data-entry-img').get().strip()
                name = td.xpath('@data-entry-name').get().strip()
                url = add_url(td.xpath('@data-entry-link').get().strip())
                description = tds[1].xpath('string(.)').get().strip()

                characters.append(
                    {
                        'icon_url': icon_url,
                        'name': name,
                        'url': url,
                        'description': description,
                    }
                )
            else:
                name = tds[0].xpath('string(.)').get().strip()
                description = tds[1].xpath('string(.)').get().strip()
                characters.append(
                    {
                        'name': name,
                        'description': description,
                    }
                )

        item['推荐角色·'] = characters

        res_info['element_data'].append(item)

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

        base_info = await self._parse_base_info(context_page, browser_context)
        res_info.update(
            {
                '基础信息': base_info,
            }
        )

        weapon_display = await self._parse_weapon_display(context_page, browser_context)
        res_info.update(
            {
                '装备展示': weapon_display,
            }
        )

        growth_info = await self._parse_growth_info(context_page, browser_context)
        res_info.update(
            {
                '成长数值': growth_info,
            }
        )

        good_description = await self._parse_good_description(
            context_page, browser_context
        )
        res_info.update(
            {
                '装备描述': good_description,
            }
        )

        weapon_extend_info = await self._parse_weapon_extend_info(
            context_page, browser_context
        )
        res_info.update(weapon_extend_info)

        recommand_character_info = await self._parse_recommand_character_info(
            context_page, browser_context
        )
        res_info.update(
            {
                '推荐角色': recommand_character_info,
            }
        )

        return res_info
