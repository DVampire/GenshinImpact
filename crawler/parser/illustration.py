import asyncio
import os
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.parser.illustraction_pages import (
    AchievementParser,
    ArtifactParser,
    CharacterParser,
    WeaponParser,
)
from crawler.utils.url import add_url

__all__ = [
    'IllustrationParser',
]


class IllustrationParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'illustration',
        name: str = 'illustration',
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

    async def _parse_character(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/25?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing character...')
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
        res_info['id'] = 'character'
        res_info['name'] = 'character'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path

        selector = Selector(text=content)

        character_list = selector.xpath('//a[@class="collection-avatar__item"]')

        img_dir = os.path.join(self.img_path, 'character')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'character')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        characters_info = []
        for idx, character in enumerate(character_list):
            href = character.xpath('./@href').extract_first()
            id = href.split('/')[4]  # Extract the character ID from the URL
            href = add_url(href)
            icon = character.xpath(
                './div[@class="collection-avatar__icon"]/@data-src'
            ).extract_first()
            name = character.xpath(
                './div[@class="collection-avatar__title"]/text()'
            ).extract_first()

            if '预告' in name:
                continue

            character_parser = CharacterParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(character_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                characters_info.extend(await self._run_batch(tasks))
                tasks = []  # Reset tasks for the next batch

        if tasks:
            characters_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in characters_info})

        logger.info('| Finish parsing character...')

        return res_info

    async def _parse_weapon(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        parse weapon (武器)
        :param page:
        :return: res_info: Dict[str, Any]
        """

        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/5?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing weapon...')
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
        res_info['id'] = 'weapon'
        res_info['name'] = 'weapon'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path

        selector = Selector(text=content)

        weapon_list = selector.xpath('//a[@class="collection-avatar__item"]')

        img_dir = os.path.join(self.img_path, 'weapon')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'weapon')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        weapons_info = []
        for idx, weapon in enumerate(weapon_list):
            href = weapon.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = weapon.xpath(
                './div[@class="collection-avatar__icon"]/@data-src'
            ).extract_first()
            name = weapon.xpath(
                './div[@class="collection-avatar__title"]/text()'
            ).extract_first()

            weapon_parser = WeaponParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(weapon_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                weapons_info.extend(await self._run_batch(tasks))
                tasks = []  # Reset tasks for the next batch

        if tasks:
            weapons_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in weapons_info})

        return res_info

    async def _parse_artifact(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        """
        parse 圣遗物
        :param context_page:
        :param browser_context:
        :return:
        """

        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/218?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing artifact...')
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
        res_info['id'] = 'artifact'
        res_info['name'] = 'artifact'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path

        selector = Selector(text=content)

        artifact_list = selector.xpath('//a[@class="relic-describe"]')

        img_dir = os.path.join(self.img_path, 'artifact')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'artifact')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        artifacts_info = []
        for idx, artifact in enumerate(artifact_list):
            href = artifact.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = artifact.xpath(
                './/div[@class="relic-describe__top--image"]/img/@data-src'
            ).extract_first()

            name = (
                artifact.xpath('.//div[@class="relic-describe__top--title"]/text()')
                .get()
                .strip()
            )

            artifact_parser = ArtifactParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(artifact_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                artifacts_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            artifacts_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in artifacts_info})

        return res_info

    async def _parse_achievement(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/252?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing achievement...')
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
        res_info['id'] = 'achievement'
        res_info['name'] = 'achievement'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path

        selector = Selector(text=content)

        achievement_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'achievement')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'achievement')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        achievements_info = []
        for idx, achievement in enumerate(achievement_list):
            achievement = achievement.xpath('.//a')
            href = achievement.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = achievement.xpath('.//img/@data-src').extract_first()

            name = achievement.xpath('.//a/@title').extract_first()

            achievement_parser = AchievementParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(achievement_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                achievements_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            achievements_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in achievements_info})

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

        res_info['角色'] = await self._parse_character(context_page, browser_context)

        res_info['武器'] = await self._parse_weapon(context_page, browser_context)

        res_info['圣遗物'] = await self._parse_artifact(context_page, browser_context)

        res_info['成就'] = await self._parse_achievement(context_page, browser_context)

        return res_info
