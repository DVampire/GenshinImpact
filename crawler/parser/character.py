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
    'CharacterParser',
]


class CharacterParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        page_name: str,
        character_name: str,
        icon: str,
        img_path: str,
        html_path: str,
        **kwargs,
    ) -> None:
        self.config = config
        self.url = url
        self.page_name = page_name
        self.character_name = character_name
        self.icon = icon

        self.img_path = img_path
        self.html_path = html_path

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

        ###################################Get the 基础信息##########################################
        res_base_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 基础信息 - element...')
        save_name = f'{1:04d}_基础信息'

        # Locate the matching element
        element = context_page.locator('div.obc-tmp-character__pc').first  # type: ignore

        content, img_path, html_path = await save_element(
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
        )

        # Save the results to the dictionary
        res_base_info['element_img_path'] = img_path
        res_base_info['element_html_path'] = html_path
        logger.info('| Finish parsing page - 基础信息 - element...')

        # Convert the element to scrapy selector
        element = Selector(text=content)

        logger.info('| Start parsing page - 基础信息 - sub elements...')
        # Start get sub elements
        res_base_info['element_data']: List[Dict[str, Any]] = []  # type: ignore

        item: Dict[str, Any] = dict()  # type: ignore

        character_background_img = element.css('img.bg::attr(src)').get()
        character_element_property_base64 = element.css(
            'div.top-left::attr(style)'
        ).get()
        character_name = element.css('p.obc-tmp-character__box--title::text').get()
        character_stars = len(element.css('i.obc-tmpl__rate-icon'))

        item['背景图片'] = character_background_img
        item['元素属性'] = character_element_property_base64
        item['名字'] = character_name
        item['星级'] = character_stars

        character_property_list = element.css(
            'div.obc-tmp-character__property div.obc-tmp-character__list'
        )

        for character_property in character_property_list:
            property_outer = character_property.css('div.obc-tmp-character__outer')
            for property_item in property_outer:
                key = (
                    property_item.css('div.obc-tmp-character__key::text').get().strip()
                )
                value = (
                    property_item.css('div.obc-tmp-character__value::text')
                    .get()
                    .strip()
                )
                item[key] = value

        res_base_info['element_data'].append(item)

        logger.info('| Finish parsing page - 基础信息 - sub elements...')

        res_info['base'] = res_base_info
        print(res_base_info)
        ###################################Get the base information##########################################

        swipers = await context_page.query_selector_all('div.mhy-swiper')

        ###################################Get the roleAscension#############################################
        res_role_ascension_info: Dict[str, Any] = dict()

        save_name = f'{2:04d}_角色突破'

        logger.info('| Start parsing page - 角色突破 - element...')

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-roleAscension').first

        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_height_scale=3.0,
        )

        # Save the results to the dictionary
        res_role_ascension_info['element_img_path'] = img_path
        res_role_ascension_info['element_html_path'] = html_path
        logger.info('| Finish parsing page - 角色突破 - element...')

        logger.info('| Start parsing page - 角色突破 - sub elements...')
        # Start get sub elements
        res_role_ascension_info['element_data']: List[Dict[str, Any]] = []  # type: ignore

        swiper = swipers[0]

        slides = await swiper.query_selector_all('li.swiper-pagination-bullet')
        slides_data = await swiper.query_selector_all('div.swiper-slide')

        for idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            item: Dict[str, Any] = dict()

            role_ascension_level = await slide.text_content()
            role_ascension_level = role_ascension_level.strip().replace('/', '')
            item['突破等级'] = role_ascension_level

            save_name = f'{3 + idx:04d}_角色突破_{role_ascension_level}'

            await slide.click()
            await asyncio.sleep(1)

            element = context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-roleAscension'
            ).first

            # Capture a screenshot of the element
            _, img_path, html_path = await save_element_overleaf(
                page=context_page,
                element=element,
                save_name=save_name,
                img_path=self.img_path,
                html_path=self.html_path,
                set_height_scale=3.0,
            )

            content = await slide_data.inner_html()

            # Overwrite the HTML content to a file
            save_html_file(content, html_path)

            selector = Selector(text=content)

            # Get the ascension materials
            material_list = selector.xpath(
                '//td[@class="wiki-h3" and text()="突破材料"]/following-sibling::td//li'
            )
            materials = []
            for material in material_list:
                url = add_url(material.xpath('.//a/@href').get())
                name = (
                    material.xpath('.//span[@class="obc-tmpl__icon-text"]/text()')
                    .get()
                    .strip()
                )
                quantity = (
                    material.xpath('.//span[@class="obc-tmpl__icon-num"]/text()')
                    .get()
                    .strip()
                    .replace('*', '')
                )
                materials.append({'name': name, 'quantity': quantity, 'url': url})
            item['突破材料'] = materials

            # Get the ascension attributes
            attributes = {}
            attr_rows = selector.xpath('//tr[@class="new-breach-attr-list"]')

            if len(attr_rows) == 5:
                new_talent = attr_rows[0]
                key1 = new_talent.xpath('./td[1]/text()').get().strip()
                value1 = new_talent.xpath('./td[2]//text()').get().strip()
                image_url = new_talent.xpath(
                    './td[2]//span[@class="custom-image-view"]/@data-image-url'
                ).get()

                attributes[key1] = {
                    'name': value1,
                    'image_url': image_url,
                }

                attr_rows = attr_rows[1:]

            for row in attr_rows:
                key1 = row.xpath('./td[1]/text()').get().strip()
                value1 = row.xpath('./td[2]//text()').get().strip()
                key2 = row.xpath('./td[3]/text()').get().strip()
                value2 = row.xpath('./td[4]//text()').get().strip()

                attributes[key1] = value1
                attributes[key2] = value2
            item['属性信息'] = attributes

            res_role_ascension_info['element_data'].append(item)

        logger.info('| Finish parsing page - 角色突破 - sub elements...')

        return res_info
