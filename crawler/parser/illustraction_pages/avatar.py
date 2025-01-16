from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.utils.element import save_element_overleaf

__all__ = [
    'AvatarParser',
]


class AvatarParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'avatar',
        name: str = 'avatar',
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

        # Locate the matching element
        element = context_page.locator(
            'table.obc-tmpl-part.obc-tmpl-materialBaseInfo'
        ).first

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

        tbody = Selector(text=content).xpath('.//tbody')

        trs = tbody.xpath('.//tr')

        icon_url = trs[0].xpath('.//td[1]//img/@src').get().strip()
        item_info['icon_url'] = icon_url

        # 名称
        name = (
            trs[0]
            .xpath('.//td[2]//div[@class="material-td-vertical-top"]/div/text()')
            .get()
            .strip()
        )
        item_info['名称'] = name

        # 预获取时长
        duration = (
            trs[1]
            .xpath('.//td[1]//div[@class="material-value-wrap"]//text()')
            .get()
            .strip()
        )
        item_info['预获取时长'] = duration

        for tr in trs[2:]:
            label = tr.xpath('.//td[1]//label/text()').get().strip().replace('：', '')
            if label == '任务详情':
                url = (
                    tr.xpath(
                        './/td[1]//div[@class="material-value-wrap-full"]//a/@href'
                    )
                    .get()
                    .strip()
                )
                text = (
                    tr.xpath(
                        './/td[1]//div[@class="material-value-wrap-full"]//a/text()'
                    )
                    .get()
                    .strip()
                )
                item_info[label] = {
                    'url': url,
                    'text': text,
                }
            elif label == '任务奖励':
                spans = tr.xpath('.//td[1]//span[@class="custom-image-view"]')
                tas = tr.xpath('.//td[1]//p//text()').getall()
                tas = [item.strip() for item in tas if item.strip()]

                names = []
                amounts = []
                for ta in tas:
                    name, amount = ta.split('*')
                    names.append(name)
                    amounts.append(int(amount))

                rewards = []
                for span, name, amount in zip(spans, names, amounts):
                    reward_name = name
                    reward_amount = amount

                    reward_icon_url = span.xpath('./@data-image-url').get().strip()

                    rewards.append(
                        {
                            'name': reward_name,
                            'amount': reward_amount,
                            'icon_url': reward_icon_url,
                        }
                    )
            else:
                value = (
                    tr.xpath('.//td[1]//div[@class="material-value-wrap-full"]//text()')
                    .get()
                    .strip()
                )
                item_info[label] = value

        res_info['data']['基础信息'] = item_info

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

        return res_info
