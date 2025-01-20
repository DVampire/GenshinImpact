import asyncio
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf

__all__ = [
    'NpcParser',
]


class NpcParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'npc',
        name: str = 'npc',
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

        # Locate the matching element
        element = context_page.locator('div.obc-tmpl-part.obc-tmpl-npcBaseInfo').first

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

        # 名称
        name = selector.xpath('.//h1[@class="wiki-h1"]/text()').get().strip()
        item_info['名称'] = name

        tbodys = selector.xpath('.//tbody')

        # base info
        tbody = tbodys[0]
        trs = tbody.xpath('.//tr')

        icon_url = trs[0].xpath('.//td[1]//img/@src').get().strip()
        item_info['icon_url'] = icon_url

        # 性别
        label = trs[0].xpath('.//td[2]//text()').get().strip()
        value = trs[0].xpath('.//td[3]//text()').get().strip()
        item_info[label] = value

        # 位置
        label = trs[1].xpath('.//td[1]//text()').get().strip()
        value = trs[1].xpath('.//td[2]//text()').get().strip()
        item_info[label] = value

        # 职业
        label = trs[2].xpath('.//td[1]//text()').get().strip()
        value = trs[2].xpath('.//td[2]//text()').get().strip()
        item_info[label] = value

        # 功能
        label = trs[3].xpath('.//td[1]//text()').get().strip()
        value = trs[3].xpath('.//td[2]//text()').get().strip()
        item_info[label] = value

        tbody = tbodys[1]

        # 编者注
        tr = tbody.xpath('.//tr[1]')
        label = tr.xpath('.//td[1]//text()').get().strip()
        value = tr.xpath('.//td[2]//text()')
        if value:
            value = value.get().strip()
        else:
            value = ''
        item_info[label] = value

        res_info['data']['基础信息'] = item_info

        return res_info

    async def _parse_map_desc_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - NPC展示 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = context_page.locator('div.obc-tmpl-part.obc-tmpl-mapDesc').first  # type: ignore

            save_name = f'{self.save_id:04d}_NPC展示'
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

            res_info['data']['NPC展示'] = item_info

            context_page.set_default_timeout(30000)

        except Exception:
            logger.info('| No element found - NPC展示 - element...')

        logger.info('| Finish parsing page - NPC展示 - element...')
        return res_info

    async def _parse_story_dialogue(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - NPC对话 - element...')

        if not element:
            # Locate the matching element
            element = context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-interactiveDialogue'
            )

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

        save_name = f'{self.save_id:04d}_NPC对话'
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

        xbox = selector.xpath('.//div[@class="tree-wrapper"]')
        item_info['内容'] = '\n'.join(xbox.xpath('.//text()').getall()).strip()
        res_info['data']['NPC对话'] = item_info

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

        res_info['NPC展示'] = await self._parse_map_desc_info(
            context_page=context_page, browser_context=browser_context
        )

        res_info['NPC对话'] = await self._parse_story_dialogue(
            context_page=context_page, browser_context=browser_context
        )

        return res_info
