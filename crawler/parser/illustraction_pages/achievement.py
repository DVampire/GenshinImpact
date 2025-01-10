from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf
from crawler.utils.url import add_url

__all__ = [
    'AchievementParser',
]


class AchievementParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'achievement',
        name: str = 'achievement',
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
            'table.obc-tmpl-part.obc-tmpl-materialBaseInfo'
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

        trs = tbody.xpath('.//tr')

        item_info['icon_url'] = trs[0].xpath('./td[1]//img/@src').get().strip()

        label = trs[0].xpath('./td[2]/div/label/text()').get().strip().replace('：', '')
        value = trs[0].xpath('./td[2]/div/div/text()').get().strip()
        item_info[label] = value  # 名称

        label = trs[1].xpath('./td[1]/div/label/text()').get().strip().replace('：', '')
        value = trs[1].xpath('./td[1]/div/div//p//text()').get().strip()
        item_info[label] = value  # 成就集

        label = (
            trs[2].xpath('./td[1]/div//strong/text()').get().strip().replace('：', '')
        )
        value = (
            trs[2]
            .xpath('./td[1]/div//p//text()')
            .getall()[-1]
            .strip()
            .replace('：', '')
        )
        item_info[label] = value  # 成就描述

        label = (
            trs[3].xpath('./td[1]/div//strong/text()').get().strip().replace('：', '')
        )
        spans = trs[3].xpath('./td[1]//span[@class="custom-entry-wrapper"]')
        values = []
        for span in spans:
            value = {
                'icon_url': span.xpath('./@data-entry-img').get().strip(),
                'name': span.xpath('./@data-entry-name').get().strip(),
                'amount': span.xpath('./@data-entry-amount').get().strip(),
                'url': add_url(span.xpath('./@data-entry-link').get().strip()),
            }
            values.append(value)
        item_info[label] = values  # 达成奖励

        label = (
            trs[4].xpath('./td[1]/div//strong/text()').get().strip().replace('：', '')
        )
        value = (
            trs[4]
            .xpath('./td[1]/div//p//text()')
            .getall()[-1]
            .strip()
            .replace('：', '')
        )
        item_info[label] = value  # 上线版本

        if len(trs) > 5:
            label = (
                trs[5]
                .xpath('./td[1]/div//strong/text()')
                .get()
                .strip()
                .replace('：', '')
            )
            spans = trs[5].xpath('./td[1]//span[@class="custom-entry-wrapper"]')

            values = []
            for span in spans:
                value = {
                    'icon_url': span.xpath('./@data-entry-img').get().strip(),
                    'name': span.xpath('./@data-entry-name').get().strip(),
                    'url': add_url(span.xpath('./@data-entry-link').get().strip()),
                }
                values.append(value)

            item_info[label] = values  # 成就相关

        res_info['data']['基础信息'] = item_info

        logger.info('| Finish parsing page - 基础信息 - element...')

        return res_info

    async def _pase_recommend_strategy_info(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        logger.info('| Start parsing page - 攻略推荐 - element...')

        try:
            context_page.set_default_timeout(2000)

            element = context_page.locator(
                'div.wiki-consumer-module-strategy.obc-tmpl-part.obc-tmpl-strategy'
            ).first  # type: ignore

            save_name = f'{self.save_id:04d}_攻略推荐'
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
                    strategy.xpath(
                        './a/div[@class="obc-tmpl-strategy__card--text"]/text()'
                    )
                    .get()
                    .strip()
                )

                item_info[strategy_title] = {
                    'title': strategy_title,
                    'url': strategy_url,
                    'image_url': strategy_image_url,
                }

            res_info['data']['攻略推荐'] = item_info

            context_page.set_default_timeout(30000)
        except Exception:
            logger.info('| No element found - 攻略推荐 - element...')

        logger.info('| Finish parsing page - 攻略推荐 - element...')
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

        recommend_strategy_info = await self._pase_recommend_strategy_info(
            context_page, browser_context
        )
        if recommend_strategy_info:
            res_info['攻略推荐'] = recommend_strategy_info

        return res_info
