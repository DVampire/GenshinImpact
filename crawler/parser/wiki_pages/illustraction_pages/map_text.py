import asyncio
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.url import add_url

__all__ = [
    'MapTextParser',
]


class MapTextParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'map_text',
        name: str = 'map_text',
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

    async def _parse_map_desc_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 图片展示 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = context_page.locator('div.obc-tmpl-part.obc-tmpl-mapDesc').first  # type: ignore

            save_name = f'{self.save_id:04d}_图片展示'
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

            res_info['data']['图片展示'] = item_info

            context_page.set_default_timeout(30000)

        except Exception:
            logger.info('| No element found - 图片展示 - element...')

        logger.info('| Finish parsing page - 图片展示 - element...')
        return res_info

    async def _parse_corresponding_task_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 相关任务 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = context_page.locator(
                'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
            ).first  # type: ignore

            save_name = f'{self.save_id:04d}_相关任务'
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

            item_info: Dict[str, Any] = dict()

            selector = Selector(text=content)

            xbox = selector.xpath('.//div[@class="obc-tmpl__paragraph-box  "]')

            ups = xbox.xpath('./p | ./ul')

            groups: List[List[Selector]] = []
            group: List[Selector] = []
            for element in ups:
                tag_name = element.root.tag
                if tag_name == 'p':
                    if group:
                        groups.append(group)
                        group = []
                    group.append(element)
                elif tag_name == 'ul':
                    group.append(element)
            if group:
                groups.append(group)

            for group in groups:
                title = (
                    group[0].xpath('.//strong/text()').get().strip().replace('：', '')
                )

                spans = group[1].xpath('.//span[@class="custom-entry-wrapper"]')
                tasks = []
                for span in spans:
                    task = span.xpath('./@data-entry-name').get().strip()
                    image_url = span.xpath('./@data-entry-img').get().strip()
                    url = add_url(span.xpath('./@data-entry-link').get().strip())
                    tasks.append(
                        {
                            'name': task,
                            'image_url': image_url,
                            'url': url,
                        }
                    )

                item_info[title] = tasks

            res_info['data']['相关任务'] = item_info

            context_page.set_default_timeout(30000)

        except Exception:
            logger.info('| No element found - 相关任务 - element...')

        logger.info('| Finish parsing page - 相关任务 - element...')
        return res_info

    async def _parse_interactive_dialogue(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 交互文本 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = context_page.locator(
                'div.obc-tmpl-part.obc-tmpl-interactiveDialogue'
            ).first  # type: ignore

            save_name = f'{self.save_id:04d}_交互文本'
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

            selector = Selector(text=content)

            item_info: Dict[str, Any] = dict()

            content = '\n'.join(selector.xpath('.//text()').getall()).strip()

            item_info['内容'] = content

            res_info['data']['交互文本'] = item_info

            context_page.set_default_timeout(30000)

        except Exception:
            logger.info('| No element found - 交互文本 - element...')

        logger.info('| Finish parsing page - 交互文本 - element...')

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

        res_info['图片展示'] = await self._parse_map_desc_info(
            context_page=context_page, browser_context=browser_context
        )

        res_info['相关任务'] = await self._parse_corresponding_task_info(
            context_page=context_page, browser_context=browser_context
        )

        res_info['交互文本'] = await self._parse_interactive_dialogue(
            context_page=context_page, browser_context=browser_context
        )

        return res_info
