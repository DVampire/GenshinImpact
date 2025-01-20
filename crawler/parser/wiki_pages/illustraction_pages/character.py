import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.html_files import save_html_file
from crawler.utils.url import add_url

__all__ = [
    'CharacterParser',
]


@dataclass(order=True)
class Voice:
    # Define fields
    lan_idx: int = field(
        compare=True
    )  # Included in comparison (primary key for sorting)
    but_idx: int = field(
        compare=True
    )  # Included in comparison (secondary key for sorting)
    language: str = field(compare=False)  # Excluded from comparison
    name: str = field(compare=False)  # Excluded from comparison
    url: str = field(compare=False)  # Excluded from comparison
    content: str = field(compare=False)  # Excluded from comparison

    # Custom hash based only on lan_idx and but_idx
    def __hash__(self):
        return hash((self.lan_idx, self.but_idx))

    # Custom equality to match the hash logic
    def __eq__(self, other):
        if not isinstance(other, Voice):
            return NotImplemented
        return self.lan_idx == other.lan_idx and self.but_idx == other.but_idx


class CharacterParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'character',
        name: str = 'character',
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
        element = context_page.locator('div.obc-tmp-character__pc').first  # type: ignore

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

        character_background_img = element.css('img.bg::attr(src)').get()
        character_element_property_base64 = element.css(
            'div.top-left::attr(style)'
        ).get()
        character_name = element.css('p.obc-tmp-character__box--title::text').get()
        character_stars = len(element.css('i.obc-tmpl__rate-icon'))

        item_info['背景图片'] = character_background_img
        item_info['元素属性'] = character_element_property_base64
        item_info['名字'] = character_name
        item_info['星级'] = character_stars

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
                item_info[key] = value

        res_info['data']['基础信息'] = item_info

        logger.info('| Finish parsing page - 基础信息 - element...')

        return res_info

    async def _parse_role_ascension_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_角色突破'
        self.save_id += 1

        logger.info('| Start parsing page - 角色突破 - element...')

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-roleAscension').first

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

            role_ascension_level = await slide.text_content()
            role_ascension_level = role_ascension_level.strip().replace('/', '')
            item_info['突破等级'] = role_ascension_level

            save_name = f'{self.save_id:04d}_角色突破_{role_ascension_level}'
            self.save_id += 1

            await slide.click()
            await asyncio.sleep(1)

            element = context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-roleAscension'
            ).first

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

            # Get the ascension materials
            material_list = selector.xpath(
                '//td[@class="wiki-h3" and text()="突破材料"]/following-sibling::td//li'
            )
            materials = []
            for material in material_list:
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
                    {'name': name, 'amount': amount, 'url': url, 'icon_url': icon_url}
                )
            item_info['突破材料'] = materials

            # Get the ascension attributes
            attributes = {}
            attr_rows = selector.xpath('//tr[@class="new-breach-attr-list"]')

            if len(attr_rows) == 5:
                new_talent = attr_rows[0]
                key1 = new_talent.xpath('./td[1]/text()').get().strip()
                value1 = new_talent.xpath('./td[2]//text()').get().strip()
                icon_url = new_talent.xpath(
                    './td[2]//span[@class="custom-image-view"]/@data-image-url'
                ).get()

                attributes[key1] = {
                    'name': value1,
                    'icon_url': icon_url,
                }

                attr_rows = attr_rows[1:]

            for row in attr_rows:
                key1 = row.xpath('./td[1]/text()').get().strip()
                value1 = row.xpath('./td[2]//text()').get().strip()
                key2 = row.xpath('./td[3]/text()').get().strip()
                value2 = row.xpath('./td[4]//text()').get().strip()

                attributes[key1] = value1
                attributes[key2] = value2

            item_info['属性信息'] = attributes

            res_info['data'][role_ascension_level] = item_info

        logger.info('| Finish parsing page - 角色突破 - element...')

        return res_info

    async def _parse_recommend_equipment_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_推荐装备'
        self.save_id += 1

        logger.info('| Start parsing page - 推荐装备 - element...')

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-recommend').first

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

        # 武器推荐
        slide = slides[0]
        slide_data = slides_data[0]

        item_info: Dict[str, Any] = dict()

        await slide.click()
        await asyncio.sleep(1)

        save_name = f'{self.save_id:04d}_推荐装备_武器推荐'

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-recommend').first

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

        save_html_file(content, html_path)

        item_info['img_path'] = img_path
        item_info['html_path'] = html_path

        selector = Selector(text=content)

        weapon_list = selector.xpath('//tr')
        for weapon in weapon_list[1:]:
            weapon_name = weapon.xpath(
                './td[1]//span[@class="custom-entry-wrapper"]/@data-entry-name'
            ).get()
            weapon_url = add_url(
                weapon.xpath(
                    './td[1]//span[@class="custom-entry-wrapper"]/@data-entry-link'
                ).get()
            )
            weapon_icon_url = weapon.xpath(
                './td[1]//span[@class="custom-entry-wrapper"]/@data-entry-img'
            ).get()
            weapon_reason = weapon.xpath('./td[2]//text()').get().strip()

            item_info[weapon_name] = {
                'name': weapon_name,
                'url': weapon_url,
                'icon_url': weapon_icon_url,
                'reason': weapon_reason,
            }

        res_info['data']['武器推荐'] = item_info

        # 圣遗物推荐
        slide = slides[1]
        slide_data = slides_data[1]

        item_info: Dict[str, Any] = dict()

        await slide.click()
        await asyncio.sleep(1)

        save_name = f'{self.save_id:04d}_推荐装备_圣遗物推荐'

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-recommend').first

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

        save_html_file(content, html_path)

        item_info['img_path'] = img_path
        item_info['html_path'] = html_path

        selector = Selector(text=content)

        artifact_list = selector.xpath('//tr')

        for artifact in artifact_list[1:]:
            artifact_name = artifact.xpath(
                './td[1]//span[@class="custom-entry-wrapper"]/@data-entry-name'
            ).get()
            artifact_url = add_url(
                artifact.xpath(
                    './td[1]//span[@class="custom-entry-wrapper"]/@data-entry-link'
                ).get()
            )
            artifact_icon_url = artifact.xpath(
                './td[1]//span[@class="custom-entry-wrapper"]/@data-entry-img'
            ).get()
            artifact_reason = artifact.xpath('./td[2]//text()').get().strip()

            item_info[artifact_name] = {
                'name': artifact_name,
                'url': artifact_url,
                'icon_url': artifact_icon_url,
                'reason': artifact_reason,
            }

        res_info['data']['圣遗物推荐'] = item_info

        logger.info('| Finish parsing page - 推荐装备 - element...')

        return res_info

    async def _pase_recommend_strategy_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_推荐攻略'
        self.save_id += 1

        logger.info('| Start parsing page - 推荐攻略 - element...')

        element = context_page.locator(
            'div.wiki-consumer-module-strategy.obc-tmpl-part.obc-tmpl-strategy'
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

        item_info: Dict[str, Any] = dict()

        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=self.config.set_width_scale,
            set_height_scale=self.config.set_height_scale,
        )

        item_info['img_path'] = img_path
        item_info['html_path'] = html_path

        selector = Selector(text=content)

        strategy_list = selector.xpath('//div[@class="obc-tmpl-strategy__card"]')
        for strategy in strategy_list:
            strategy_url = add_url(strategy.xpath('./a/@href').get())
            strategy_image_url = strategy.xpath(
                './a/div[@class="wiki-consumer-better-image"]/picture/source/@srcset'
            ).get()
            strategy_title = (
                strategy.xpath('./a/div[@class="obc-tmpl-strategy__card--text"]/text()')
                .get()
                .strip()
            )

            item_info[strategy_title] = {
                'title': strategy_title,
                'url': strategy_url,
                'image_url': strategy_image_url,
            }

        res_info['data']['推荐攻略'] = item_info

        logger.info('| Finish parsing page - 推荐攻略 - element...')
        return res_info

    async def _parse_talent_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_天赋'
        self.save_id += 1

        logger.info('| Start parsing page - 天赋 - element...')

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-roleTalent').first

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

            talent_level = await slide.text_content()
            talent_level = talent_level.strip().replace('/', '')
            item_info['天赋等级'] = talent_level

            save_name = f'{self.save_id:04d}_天赋_{talent_level}'
            self.save_id += 1

            await slide.click()
            await asyncio.sleep(1)

            element = context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-roleTalent'
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

            content = await slide_data.inner_html()

            save_html_file(content, html_path)

            item_info['img_path'] = img_path
            item_info['html_path'] = html_path

            selector = Selector(text=content)

            attack_talent_icon_url = (
                selector.xpath('//img[@class="obc-tmpl__icon"]/@src').get().strip()
            )
            attack_talent_name = (
                selector.xpath('//span[@class="obc-tmpl__icon-text"]/text()')
                .get()
                .strip()
            )
            attack_talent_description = (
                selector.xpath(
                    '//p[@class="obc-tmpl__paragraph-box obc-tmpl__pre-text"]/text()'
                )
                .get()
                .strip()
            )

            item_info['攻击天赋'] = {
                'icon_url': attack_talent_icon_url,
                'name': attack_talent_name,
                'description': attack_talent_description,
            }

            # 详细属性
            xbox = selector.xpath('//div[@class="obc-tmpl__scroll-x-box"]')

            thead = xbox.xpath('.//thead')
            tbody = xbox.xpath('.//tbody')

            levels = thead.xpath('.//th//text()').getall()
            levels = [level.strip() for level in levels if level.strip()]

            if len(levels) == 1:
                details = tbody.xpath('.//p').xpath('string(.)').get().strip()
                item_info['详细属性'] = details
            else:
                details = tbody.xpath('./tr')

                item_info['详细属性'] = []
                for idx, detail in enumerate(details[:-1]):
                    tds = detail.xpath('./td')

                    td_name = tds[0].xpath('.//p').xpath('string(.)').get()
                    td_values = [
                        td.xpath('.//p').xpath('string(.)').get(default='')
                        for td in tds[1:]
                    ]
                    td_values = [
                        td.strip() for td in td_values[: len(levels)]
                    ]  # 有些天赋等级没有对应的属性

                    item_info['详细属性'].append(
                        {
                            'name': td_name,
                            'values': {
                                level: value
                                for level, value in zip(levels[1:], td_values)
                            },
                        }
                    )

                # 升级材料
                tds = details[-1].xpath('./td')

                td_name = tds[0].xpath('.//p').xpath('string(.)').get()
                tds = tds[1:]  # 去掉第一个td
                tds = tds[: len(levels)]  # 有些天赋等级没有对应的属性

                materials_list = []
                for idx, td in enumerate(tds):
                    if td.xpath('.//span[@class="custom-entry-wrapper"]'):
                        url = add_url(
                            td.xpath(
                                './/span[@class="custom-entry-wrapper"]/@data-entry-link'
                            ).get()
                        )
                        name = td.xpath(
                            './/span[@class="custom-entry-wrapper"]/@data-entry-name'
                        ).get()
                        icon_url = td.xpath(
                            './/span[@class="custom-entry-wrapper"]/@data-entry-img'
                        ).get()
                        amount = td.xpath(
                            './/span[@class="custom-entry-wrapper"]/@data-entry-amount'
                        ).get()

                        materials_list.append(
                            {
                                'url': url,
                                'name': name,
                                'icon_url': icon_url,
                                'amount': amount,
                            }
                        )
                    elif td.xpath('.//p').xpath('string(.)').get().strip():
                        materials_list.append(
                            td.xpath('.//p').xpath('string(.)').get().strip()
                        )
                    else:
                        materials_list.append({})

                materials_dict = {
                    level: material
                    for level, material in zip(levels[1:], materials_list)
                }
                item_info['升级材料'] = {
                    'name': td_name,
                    'values': materials_dict,
                }

            res_info['data'][talent_level] = item_info

        logger.info('| Finish parsing page - 天赋 - element...')

        return res_info

    async def _parse_constellation_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_命之座'
        self.save_id += 1

        logger.info('| Start parsing page - 命之座 - element...')

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

        xbox = Selector(text=content)
        tbody = xbox.xpath('.//tbody')

        item_info: Dict[str, Any] = dict()

        for idx, tr in enumerate(tbody.xpath('.//tr')):
            icon_url = tr.xpath(
                './/td[1]//span[@class="custom-image-view"]/@data-image-url'
            ).get()
            name = tr.xpath('.//td[1]//p').xpath('string(.)').get().strip()
            description = '\n'.join(
                tr.xpath('.//td[2]//p').xpath('string(.)').getall()
            ).strip()

            item_info[name] = {
                'icon_url': icon_url,
                'name': name,
                'description': description,
            }

        res_info['data']['命之座'] = item_info

        logger.info('| Finish parsing page - 命之座 - element...')

        return res_info

    async def _parse_character_display_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 角色展示 - element...')

        elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-mapDesc'
        ).all()

        # parse element 1
        res_element_1_info: Dict[str, Any] = dict()
        element = elements[0]

        save_name = f'{self.save_id:04d}_角色展示_1'
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

        res_element_1_info['img_path'] = img_path
        res_element_1_info['html_path'] = html_path
        res_element_1_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()
        item_info['角色展示'] = selector.xpath('.//source/@srcset').get()
        res_element_1_info['data'] = item_info

        # parse element 2
        res_element_2_info: Dict[str, Any] = dict()

        element = elements[1]

        save_name = f'{self.save_id:04d}_角色展示_2'
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

        res_element_2_info['img_path'] = img_path
        res_element_2_info['html_path'] = html_path
        res_element_2_info['data']: Dict[str, Any] = dict()  # type: ignore

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

            save_name = f'{self.save_id:04d}_角色展示_2_{idx}'
            self.save_id += 1

            element = await context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-mapDesc'
            ).all()
            element = element[1]

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
            name = await slide.text_content()
            image_url = await slide_data.locator('source').first.get_attribute('srcset')

            item_info['name'] = name
            item_info['image_url'] = image_url

            res_element_2_info['data'][name] = item_info

        # parse element 3
        res_element_3_info: Dict[str, Any] = dict()

        element = elements[2]

        save_name = f'{self.save_id:04d}_角色展示_3'
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

        res_element_3_info['img_path'] = img_path
        res_element_3_info['html_path'] = html_path
        res_element_3_info['data']: Dict[str, Any] = dict()  # type: ignore

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

            save_name = f'{self.save_id:04d}_角色展示_3_{idx}'
            self.save_id += 1

            element = await context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-mapDesc'
            ).all()
            element = element[2]

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

            name = await slide.text_content()
            image_url = await slide_data.locator('source').first.get_attribute('srcset')

            item_info['name'] = name
            item_info['image_url'] = image_url

            res_element_3_info['data'][name] = item_info

        logger.info('| Finish parsing page - 角色展示 - element...')

        res_info['角色展示1'] = res_element_1_info
        res_info['角色展示2'] = res_element_2_info
        res_info['角色展示3'] = res_element_3_info

        return res_info

    async def _parse_bussiness_card_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_名片'
        self.save_id += 1

        logger.info('| Start parsing page - 名片 - element...')

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-businessCard').first

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

        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        item_info['image_url'] = selector.xpath('.//source/@srcset').get()

        res_info['data']['名片'] = item_info

        logger.info('| Finish parsing page - 名片 - element...')

        return res_info

    async def _parse_speciality_cuisine(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_特殊料理'
        self.save_id += 1

        logger.info('| Start parsing page - 特殊料理 - element...')

        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()
        # filter the element
        element = None
        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').first.text_content()
            if '特殊料理' in title:
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

        item_info['icon_url'] = selector.xpath('.//source/@srcset').get()
        item_info['name'] = selector.xpath('.//p[1]//a/text()').get().strip()
        item_info['url'] = selector.xpath('.//p[1]//a/@href').get().strip()
        item_info['description'] = selector.xpath('.//p[2]//text()').get().strip()

        res_info['data']['特殊料理'] = item_info

        logger.info('| Finish parsing page - 特殊料理 - element...')

        return res_info

    async def _parse_character_cv_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_角色CV'
        self.save_id += 1

        logger.info('| Start parsing page - 角色CV - element...')

        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()

        # filter the element
        element = None
        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').first.text_content()
            if '角色CV' in title:
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
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        cv_info = selector.xpath('//div[@class="obc-tmpl__paragraph-box  "]//table//tr')
        for cv in cv_info:
            cv_type = cv.xpath('./td[1]//text()').get().strip().replace('：', '')
            cv_name = cv.xpath('./td[2]//text()').get().strip()

            item_info[cv_type] = cv_name

        res_info['data']['角色CV'] = item_info

        logger.info('| Finish parsing page - 角色CV - element...')

        return res_info

    async def _parse_character_extend_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 角色扩展 - element...')

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
                    set_width_scale=1.0,
                    set_height_scale=3.0,
                )

                res_info[title]: Dict[str, Any] = dict()
                res_info[title]['img_path'] = img_path
                res_info[title]['html_path'] = html_path
                res_info[title]['data']: Dict[str, Any] = dict()

                selector = Selector(text=content)

                item_info: Dict[str, Any] = dict()

                item_info['description'] = ''.join(
                    selector.xpath('.//p').xpath('string(.)').getall()
                ).strip()

                res_info[title]['data']['内容'] = item_info

        logger.info('| Finish parsing page - 角色扩展 - element...')
        return res_info

    async def _parse_voice_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_配音展示'
        self.save_id += 1

        logger.info('| Start parsing page - 配音展示 - element...')

        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-roleVoice').first

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

        # voices = []
        # async def log_request(request, name, language, content, lan_idx, but_idx):
        #     url = request.url
        #
        #     if 'mp3' in url:
        #         voice= Voice(language=language,
        #                      name=name,
        #                      url=url,
        #                      content=content,
        #                      lan_idx=lan_idx,
        #                      but_idx=but_idx)
        #         voices.append(voice)
        #     else:
        #         logger.info(f'| {url} {name} {language} {content} {lan_idx} {but_idx}')

        for lan_idx, (slide, slide_data) in enumerate(zip(slides, slides_data)):
            item_info: Dict[str, Any] = dict()

            language = await slide.text_content()

            await slide.click()
            await asyncio.sleep(1)

            content = await slide_data.inner_html()

            buttons = await slide_data.locator(
                'div.obc-tmpl-character__voice-btn'
            ).all()

            selector = Selector(text=content)

            trs = selector.xpath('.//tr')

            for but_idx, (tr, button) in enumerate(zip(trs, buttons)):
                voice_name = tr.xpath('./td[1]//text()').get().strip()
                voice_content = ''.join(
                    tr.xpath('.//span[@class="obc-tmpl-character__voice-content"]')
                    .xpath('string(.)')
                    .getall()
                ).strip()

                # async def log_request_warpper(request):
                #     await log_request(request,
                #                       voice_name,
                #                       language,
                #                       voice_content,
                #                       lan_idx,
                #                       but_idx)
                #
                # context_page.on('request', log_request_warpper)
                # await button.scroll_into_view_if_needed()
                # await button.click(force=True)

                item_info[str(but_idx)] = {'name': voice_name, 'content': voice_content}

            res_info['data'][language] = item_info

        logger.info('| Finish parsing page - 配音展示 - element...')
        return res_info

    async def _parse_correlation_voice_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_角色关联语音'
        self.save_id += 1

        logger.info('| Start parsing page - 角色关联语音 - element...')

        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()

        # filter the element
        element = None
        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').first.text_content()
            if '角色关联语音' in title:
                element = ele
                break

        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=1.0,
            set_height_scale=3.0,
        )

        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        tbody = selector.xpath('.//tbody')
        correlation_characters = tbody.xpath('.//tr')

        item_info: Dict[str, Any] = dict()

        for character in correlation_characters[1:]:  # skip the first one
            character_info = character.xpath(
                './td[1]//span[@class="custom-entry-wrapper"]'
            )
            character_url = add_url(
                character_info.xpath('./@data-entry-link').get().strip()
            )
            character_icon_url = character_info.xpath('./@data-entry-img').get().strip()
            character_name = character_info.xpath('./@data-entry-name').get().strip()

            voice_content = ''.join(
                character.xpath('./td[2]//p').xpath('string(.)').getall()
            ).strip()

            item_info[character_name] = {
                'url': character_url,
                'icon_url': character_icon_url,
                'content': voice_content,
                'name': character_name,
            }

        res_info['data'] = item_info

        logger.info('| Finish parsing page - 角色关联语音 - element...')

        return res_info

    async def _parse_timeline_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_角色宣发时间轴'
        self.save_id += 1

        logger.info('| Start parsing page - 角色宣发时间轴 - element...')

        element = context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-timelineBaseInfo'
        ).first

        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=1.0,
            set_height_scale=4.0,
        )

        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        timeline_items = selector.xpath('.//div[@class="timeline-content"]')
        for timeline_item in timeline_items:
            time = timeline_item.xpath('.//h3//text()').get().strip()
            title = timeline_item.xpath('.//h4//text()').get().strip()
            # custom-image-view
            image_url = (
                timeline_item.xpath(
                    './/span[@class="custom-image-view"]/@data-image-url'
                )
                .get()
                .strip()
            )

            content = ''.join(
                timeline_item.xpath('.//p').xpath('string(.)').getall()
            ).strip()
            url = timeline_item.xpath('.//a/@href').get().strip()

            item_info[time] = {
                'time': time,
                'title': title,
                'image_url': image_url,
                'content': content,
                'url': url,
            }

        res_info['data']['角色宣发时间轴'] = item_info

        logger.info('| Finish parsing page - 角色宣发时间轴 - element...')

        return res_info

    async def _parse_media_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_角色媒体资料'
        self.save_id += 1

        logger.info('| Start parsing page - 角色媒体资料 - element...')

        element = context_page.locator(
            'div.wiki-consumer-module-strategy.obc-tmpl-part.obc-tmpl-strategy'
        ).last

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

        cards = selector.xpath('.//div[@class="obc-tmpl-strategy__card"]')

        for card in cards:
            url = add_url(card.xpath('./a/@href').get().strip())
            image_url = card.xpath('.//source/@srcset').get().strip()
            title = (
                card.xpath('.//div[@class="obc-tmpl-strategy__card--text"]//text()')
                .get()
                .strip()
            )

            item_info[title] = {'url': url, 'image_url': image_url, 'title': title}
        res_info['data']['角色媒体资料'] = item_info

        logger.info('| Finish parsing page - 角色媒体资料 - element...')

        return res_info

    async def _parse_associated_terms_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        save_name = f'{self.save_id:04d}_关联词条'
        self.save_id += 1

        logger.info('| Start parsing page - 关联词条 - element...')

        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()

        # filter the element
        element = None
        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').first.text_content()
            if '关联词条' in title:
                element = ele
                break

        content, img_path, html_path = await save_element_overleaf(
            page=context_page,
            element=element,
            save_name=save_name,
            img_path=self.img_path,
            html_path=self.html_path,
            set_width_scale=1.0,
            set_height_scale=3.0,
        )

        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        xbox = selector.xpath('.//div[@class="obc-tmpl__paragraph-box  "]')

        ups = xbox.xpath('./ul | ./p')

        groups: List[List[Selector]] = []
        group: List[Selector] = []
        for element in ups:
            tag_name = element.root.tag
            if tag_name == 'ul':
                if group:
                    groups.append(group)
                    group = []
                group.append(element)
            elif tag_name == 'p':
                group.append(element)
        if group:
            groups.append(group)

        item_info: Dict[str, Any] = dict()

        for group in groups:
            ul = group[0]
            ps = group[1:]

            name = ul.xpath('.//p').xpath('string(.)').get().strip()

            associated_terms = []
            for p in ps:
                associated_term = p.xpath('.//span[@class="custom-entry-wrapper"]')
                if associated_term:
                    url = add_url(associated_term.xpath('./@data-entry-link').get())
                    name = associated_term.xpath('./@data-entry-name').get()
                    icon_url = associated_term.xpath('./@data-entry-img').get()

                    associated_terms.append(
                        {
                            'url': url,
                            'name': name,
                            'icon_url': icon_url,
                        }
                    )
                else:
                    associated_terms.append(p.xpath('string(.)').get().strip())

            item_info[name] = {'name': name, 'associated_terms': associated_terms}

            res_info['data']['关联词条'] = item_info

        logger.info('| Finish parsing page - 关联词条 - element...')

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

        res_info['角色突破'] = await self._parse_role_ascension_info(
            context_page, browser_context
        )

        res_info['推荐装备'] = await self._parse_recommend_equipment_info(
            context_page, browser_context
        )

        res_info['推荐攻略'] = await self._pase_recommend_strategy_info(
            context_page, browser_context
        )

        res_info['天赋'] = await self._parse_talent_info(context_page, browser_context)

        res_info['命之座'] = await self._parse_constellation_info(
            context_page, browser_context
        )

        character_display_info = await self._parse_character_display_info(
            context_page, browser_context
        )
        res_info['角色展示1'] = character_display_info['角色展示1']
        res_info['角色展示2'] = character_display_info['角色展示2']
        res_info['角色展示3'] = character_display_info['角色展示3']

        res_info['名片'] = await self._parse_bussiness_card_info(
            context_page, browser_context
        )

        res_info['特殊料理'] = await self._parse_speciality_cuisine(
            context_page, browser_context
        )

        res_info['角色CV'] = await self._parse_character_cv_info(
            context_page, browser_context
        )

        # Extend information
        character_extend_info = await self._parse_character_extend_info(
            context_page, browser_context
        )
        res_info.update(character_extend_info)

        res_info['配音展示'] = await self._parse_voice_info(
            context_page, browser_context
        )

        res_info['角色关联语音'] = await self._parse_correlation_voice_info(
            context_page, browser_context
        )

        res_info['角色宣发时间轴'] = await self._parse_timeline_info(
            context_page, browser_context
        )

        res_info['角色媒体资料'] = await self._parse_media_info(
            context_page, browser_context
        )

        res_info['关联词条'] = await self._parse_associated_terms_info(
            context_page, browser_context
        )

        return res_info
