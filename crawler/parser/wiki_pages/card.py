import asyncio
import os
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.parser.wiki_pages.card_pages import (
    ActionCardParser,
    CharacterCardParser,
    MonsterCardParser,
)
from crawler.utils.url import add_url

__all__ = [
    'CardParser',
]


class CardParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'card',
        name: str = 'card',
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

    async def _parse_character_card(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/231/233?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing character card...')
        save_name = f'{self.save_id:04d}_full'
        self.save_id += 1

        # Save a screenshot of the page
        content, img_path, html_path = await self._save_screenshot(
            context_page=context_page,
            save_name=save_name,
            browser_context=browser_context,
            save_screen=self.save_screen,
        )

        # Save the results to the dictionary
        res_info['url'] = self.url
        res_info['id'] = 'character_card'
        res_info['name'] = 'character_card'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        character_card_list = selector.xpath(
            '//div[@class="position-list position-list--cardFilter"]'
        ).xpath('.//a[@class="card-filter__box"]')

        img_dir = os.path.join(self.img_path, 'character_card')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'character_card')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        character_cards_info = []
        for idx, character_card in enumerate(character_card_list):
            href = character_card.xpath('./@href').extract_first()
            id = href.split('/')[4]  # Extract the character ID from the URL
            href = add_url(href)

            icon = (
                character_card.xpath('.//img[@class="card-filter__img"]/@data-src')
                .get()
                .strip()
            )

            name = (
                character_card.xpath('.//p[@class="card-filter__name"]//text()')
                .get()
                .strip()
            )

            character_card_parser = CharacterCardParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(character_card_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                character_cards_info.extend(await self._run_batch(tasks))
                tasks = []  # Reset tasks for the next batch

        if tasks:
            character_cards_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in character_cards_info})

        logger.info('| Finish parsing character card...')

        return res_info

    async def _parse_action_card(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/231/234?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing action card...')
        save_name = f'{self.save_id:04d}_full'
        self.save_id += 1

        # Save a screenshot of the page
        content, img_path, html_path = await self._save_screenshot(
            context_page=context_page,
            save_name=save_name,
            browser_context=browser_context,
            save_screen=self.save_screen,
        )

        # Save the results to the dictionary
        res_info['url'] = self.url
        res_info['id'] = 'action_card'
        res_info['name'] = 'action_card'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        action_card_list = selector.xpath(
            '//div[@class="position-list position-list--cardFilter"]'
        ).xpath('.//a[@class="card-filter__box"]')

        img_dir = os.path.join(self.img_path, 'action_card')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'action_card')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        action_cards_info = []
        for idx, action_card in enumerate(action_card_list):
            href = action_card.xpath('./@href').extract_first()
            id = href.split('/')[4]
            href = add_url(href)

            icon = (
                action_card.xpath('.//img[@class="card-filter__img"]/@data-src')
                .get()
                .strip()
            )
            name = (
                action_card.xpath('.//p[@class="card-filter__name"]//text()')
                .get()
                .strip()
            )

            action_card_parser = ActionCardParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(action_card_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                action_cards_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            action_cards_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in action_cards_info})

        logger.info('| Finish parsing action card...')

        return res_info

    async def _parse_monster_card(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/231/235?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing action card...')
        save_name = f'{self.save_id:04d}_full'
        self.save_id += 1

        # Save a screenshot of the page
        content, img_path, html_path = await self._save_screenshot(
            context_page=context_page,
            save_name=save_name,
            browser_context=browser_context,
            save_screen=self.save_screen,
        )

        # Save the results to the dictionary
        res_info['url'] = self.url
        res_info['id'] = 'monster_card'
        res_info['name'] = 'monster_card'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        action_card_list = selector.xpath(
            '//div[@class="position-list position-list--cardFilter"]'
        ).xpath('.//a[@class="card-filter__box"]')

        img_dir = os.path.join(self.img_path, 'monster_card')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'monster_card')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        monster_cards_info = []
        for idx, action_card in enumerate(action_card_list):
            href = action_card.xpath('./@href').extract_first()
            id = href.split('/')[4]
            href = add_url(href)

            icon = (
                action_card.xpath('.//img[@class="card-filter__img"]/@data-src')
                .get()
                .strip()
            )
            name = (
                action_card.xpath('.//p[@class="card-filter__name"]//text()')
                .get()
                .strip()
            )

            action_card_parser = MonsterCardParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(action_card_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                monster_cards_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            monster_cards_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in monster_cards_info})

        logger.info('| Finish parsing monster card...')

        return res_info

    async def _run_batch(self, tasks):
        """
        Run a batch of tasks and handle any potential errors.
        """
        return await asyncio.gather(*tasks)

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

        res_info['角色牌'] = await self._parse_character_card(
            context_page, browser_context
        )

        res_info['行动牌'] = await self._parse_action_card(
            context_page, browser_context
        )

        res_info['魔物牌'] = await self._parse_monster_card(
            context_page, browser_context
        )

        return res_info
