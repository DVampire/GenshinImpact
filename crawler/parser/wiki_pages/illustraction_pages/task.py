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
    'TaskParser',
]


class TaskParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'task',
        name: str = 'task',
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
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 基础信息 - element...')

        if not element:
            # Locate the matching element
            element = context_page.locator('div.obc-tmpl-part.obc-tmpl-baseInfo')

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

        trs = selector.xpath('.//tbody//tr')
        for tr in trs:
            key = tr.xpath('.//td[1]/text()').get().strip()
            value = tr.xpath('.//td[2]/text()').get().strip()
            item_info[key] = value

        res_info['data']['基础信息'] = item_info

        return res_info

    async def _parse_task_overview(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 任务概述 - element...')

        if not element:
            # Locate the matching element
            element = context_page.locator('div.obc-tmpl-part.obc-tmpl-richBaseInfo')

        save_name = f'{self.save_id:04d}_任务概述'
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

        rows = selector.xpath('.//tbody//tr')
        for row in rows:
            key = row.xpath('.//td[1]//text()').get().strip()

            span = row.xpath('.//td[2]//span[@class="custom-entry-wrapper"]')

            if span:
                name = span.xpath('./@data-entry-name').get().strip()
                icon_url = span.xpath('./@data-entry-img').get().strip()

                url = span.xpath('./@data-entry-link').get().strip()
                if '无' in url:
                    url = ''
                else:
                    url = add_url(url)
                content = ''.join(span.xpath('.//text()').getall()).strip()

                item_info[key] = {
                    'name': name,
                    'icon_url': icon_url,
                    'url': url,
                    'content': content,
                }
            else:
                content = row.xpath('.//td[2]//text()').get().strip()
                item_info[key] = content

        res_info['data']['任务概述'] = item_info

        return res_info

    async def _parse_task_process(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 任务过程 - element...')

        if not element:
            # Locate the matching element
            elements = await context_page.locator(
                'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
            ).all()

            for ele in elements:
                title = await ele.locator('div.obc-tmpl-fold__title').text_content()
                if '任务过程' in title:
                    element = ele
                    break

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

        xbox = selector.xpath('.//div[contains(@class, "obc-tmpl__paragraph-box")]')
        item_info['内容'] = '\n'.join(xbox.xpath('.//text()').getall()).strip()

        res_info['data']['任务过程'] = item_info

        return res_info

    async def _parse_task_reward(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 任务奖励 - element...')

        if not element:
            # Locate the matching element
            elements = await context_page.locator(
                'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
            ).all()

            # filter the element
            for ele in elements:
                title = await ele.locator('div.obc-tmpl-fold__title').text_content()
                if '任务奖励' in title:
                    element = ele
                    break

        save_name = f'{self.save_id:04d}_任务奖励'
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

        xbox = selector.xpath('.//div[contains(@class, "obc-tmpl__paragraph-box")]')
        spans = xbox.xpath('.//span[@class="custom-entry-wrapper"]')

        for span in spans:
            name = span.xpath('./@data-entry-name').get().strip()
            icon_url = span.xpath('./@data-entry-img').get().strip()
            url = add_url(span.xpath('./@data-entry-link').get().strip())

            amount = span.xpath('./@data-entry-amount').get()
            if amount:
                amount = int(amount)
            else:
                amount = 1

            item_info[name] = {
                'name': name,
                'icon_url': icon_url,
                'url': url,
                'amount': amount,
            }

        res_info['data']['任务奖励'] = item_info

        return res_info

    async def _parse_map_text(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 地图说明 - element...')

        if not element:
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

    async def _parse_story_dialogue(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 剧情对话 - element...')

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

        save_name = f'{self.save_id:04d}_剧情对话'
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
        res_info['data']['剧情对话'] = item_info

        return res_info

    async def _combine_parse(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        # 基础信息个数
        base_info_elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-baseInfo'
        ).all()
        # 任务概述个数
        task_overview_elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-richBaseInfo'
        ).all()
        # 任务过程个数
        elements = await context_page.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()
        task_process_elements = [
            ele
            for ele in elements
            if '任务过程'
            in await ele.locator('div.obc-tmpl-fold__title').text_content()
        ]
        # 任务奖励个数
        task_reward_elements = [
            ele
            for ele in elements
            if '任务奖励'
            in await ele.locator('div.obc-tmpl-fold__title').text_content()
        ]
        # 地图说明个数
        map_text_elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-mapDesc'
        ).all()
        # 剧情对话个数
        story_dialogue_elements = await context_page.locator(
            'div.obc-tmpl-part.obc-tmpl-interactiveDialogue'
        ).all()

        for idx, (
            base_info_element,
            task_overview_element,
            task_process_element,
            task_reward_element,
            map_text_element,
            story_dialogue_element,
        ) in enumerate(
            zip(
                base_info_elements,
                task_overview_elements,
                task_process_elements,
                task_reward_elements,
                map_text_elements,
                story_dialogue_elements,
            )
        ):
            name = base_info_element.locator(
                './/h2[class="wiki-2"]'
            ).first.text_content()

            base_info = await self._parse_base_info(
                context_page=context_page,
                browser_context=browser_context,
                element=base_info_element,
            )
            task_overview = await self._parse_task_overview(
                context_page=context_page,
                browser_context=browser_context,
                element=task_overview_element,
            )
            task_process = await self._parse_task_process(
                context_page=context_page,
                browser_context=browser_context,
                element=task_process_element,
            )
            task_reward = await self._parse_task_reward(
                context_page=context_page,
                browser_context=browser_context,
                element=task_reward_element,
            )
            map_text = await self._parse_map_text(
                context_page=context_page,
                browser_context=browser_context,
                element=map_text_element,
            )
            story_dialogue = await self._parse_story_dialogue(
                context_page=context_page,
                browser_context=browser_context,
                element=story_dialogue_element,
            )

            res_info[name] = {
                '基础信息': base_info,
                '任务概述': task_overview,
                '任务过程': task_process,
                '任务奖励': task_reward,
                '地图说明': map_text,
                '剧情对话': story_dialogue,
            }

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

        res_info = await self._combine_parse(
            context_page=context_page, browser_context=browser_context
        )

        return res_info
