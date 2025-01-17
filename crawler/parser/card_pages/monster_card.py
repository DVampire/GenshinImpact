import asyncio
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import element_exists, save_element_overleaf

__all__ = [
    'MonsterCardParser',
]


class MonsterCardParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'monster_card',
        name: str = 'monster_card',
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
        save_name = f'{self.save_id:04d}_基础信息'
        self.save_id += 1

        # Locate the matching element
        element = element.locator(
            'div.obc-tmpl-card__main.obc-tmpl-part.obc-tmpl-cardBaseInfo'
        ).first  # type: ignore
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

        image_url = selector.xpath('.//img[@class="main-card-img"]/@src').get().strip()
        item_info['image_url'] = image_url
        name = selector.xpath('.//p[@class="name"]//text()').get().strip()
        item_info['name'] = name

        attribute_items = selector.xpath('.//div[@class="name-item"]')
        for attribute_item in attribute_items:
            spans = attribute_item.xpath('.//span')
            label = spans[0].xpath('.//text()').get().strip().replace('：', '')
            value = spans[1].xpath('.//text()').get().strip()
            item_info[label] = value

        res_info['data']['基础信息'] = item_info

        logger.info('| Finish parsing page - 基础信息 - element...')

        return res_info

    async def _parse_general_skill(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 普通技能 - element...')
        save_name = f'{self.save_id:04d}_普通技能'
        self.save_id += 1

        # Locate the matching element
        element = element.locator(
            'div.wiki-consumer-module-card-skill.obc-tmpl-part.obc-tmpl-cardSkill'
        ).first

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
        res_info['data']: Dict[str, Any] = dict()

        # Convert the element to scrapy selector
        selector = Selector(text=content)

        item_info: Dict[str, Any] = dict()

        tbodies = selector.xpath('.//tbody')

        for tbody in tbodies:
            trs = tbody.xpath('.//tr')

            icon_url = trs[0].xpath('./td[1]//img/@src').get().strip()
            name = trs[0].xpath('./td[2]//span//text()').get().strip()
            skill_type = (
                trs[1]
                .xpath('./td[1]//span[@class="skill-type-text"]//text()')
                .get()
                .strip()
            )

            title = trs[2].xpath('./td[1]//div[@class="title"]//text()').get().strip()
            desc = ''.join(
                trs[2]
                .xpath('./td[1]//div[@class="obc-tmpl-card__desc"]//text()')
                .getall()
            ).strip()

            item_info[name] = {
                'icon_url': icon_url,
                'name': name,
                'skill_type': skill_type,
                'title': title,
                'desc': desc,
            }

        res_info['data']['普通技能'] = item_info

        logger.info('| Finish parsing page - 普通技能 - element...')

        return res_info

    async def _parse_effectiveness(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 效果描述 - element...')

        # Locate the matching element
        elements = await element.locator(
            'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
        ).all()

        if not await element_exists(elements):
            return res_info

        for ele in elements:
            title = await ele.locator('div.obc-tmpl-fold__title').text_content()
            if '效果描述' in title:
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

        save_name = f'{self.save_id:04d}_效果描述'
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

        res_info['data']['效果描述'] = item_info

        logger.info('| Finish parsing page - 效果描述 - element...')

        return res_info

    async def _parse_card_story(
        self, context_page: Page, browser_context: BrowserContext, element: Any = None
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 卡牌故事 - element...')

        if not element:
            # Locate the matching element
            elements = await element.locator(
                'div.obc-tmpl-fold.obc-tmpl-part.obc-tmpl-collapsePanel'
            ).all()

            for ele in elements:
                title = await ele.locator('div.obc-tmpl-fold__title').text_content()
                if '卡牌故事' in title:
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

        save_name = f'{self.save_id:04d}_卡牌故事'
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

        res_info['data']['卡牌故事'] = item_info

        logger.info('| Finish parsing page - 卡牌故事 - element...')

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

        elements = await context_page.locator('div.wiki-consumer-content-tab').all()  # type: ignore

        element = elements[0]

        base_info_element = element.locator(
            'div#module-135.obc-tmpl-part-wrap.obc-tmpl-part--align-left, '
            'div#module-2808.obc-tmpl-part-wrap.obc-tmpl-part--align-left'
        ).first
        if await element_exists(base_info_element):
            res_info['基础信息'] = await self._parse_base_info(
                context_page=context_page,
                browser_context=browser_context,
                element=base_info_element,
            )

        # 普通技能
        general_skill_element = element.locator(
            'div#module-136.obc-tmpl-part-wrap.obc-tmpl-part--align-right, '
            'div#module-2809.obc-tmpl-part-wrap.obc-tmpl-part--align-right'
        ).first
        if await element_exists(general_skill_element):
            res_info['普通技能'] = await self._parse_general_skill(
                context_page=context_page,
                browser_context=browser_context,
                element=general_skill_element,
            )

        return res_info
