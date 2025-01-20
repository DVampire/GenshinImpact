import asyncio
import os
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.parser.wiki_pages.illustraction_pages import (
    AbyssParser,
    AchievementParser,
    ActivityParser,
    AdventurerGuildParser,
    AnimalParser,
    ArtifactParser,
    AvatarParser,
    BackpackParser,
    BookParser,
    CardParser,
    CharacterParser,
    DomainParser,
    DressParser,
    EnemyParser,
    FairylandParser,
    FoodParser,
    MapTextParser,
    NpcParser,
    TaskParser,
    TutorialParser,
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
        res_info['data']: Dict[str, Any] = dict()

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
        res_info['data']: Dict[str, Any] = dict()

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

        logger.info('| Finish parsing weapon...')

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
        res_info['data']: Dict[str, Any] = dict()

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

        logger.info('| Finish parsing artifact...')

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
        res_info['data']: Dict[str, Any] = dict()

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

        logger.info('| Finish parsing achievement...')

        return res_info

    async def _parse_enemy(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/6?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing enemy...')

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
        res_info['id'] = 'enemy'
        res_info['name'] = 'enemy'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        enemy_list = selector.xpath('//a[@class="monster-image"]')

        img_dir = os.path.join(self.img_path, 'enemy')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'enemy')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        enemies_info = []

        for idx, enemy in enumerate(enemy_list):
            href = enemy.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = enemy.xpath(
                './/div[@class="monster-image__top--image"]/img/@data-src'
            ).extract_first()
            name = enemy.xpath(
                './/div[@class="monster-image__top--title"]/text()'
            ).extract_first()

            enemy_parser = EnemyParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(enemy_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                enemies_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            enemies_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in enemies_info})

        logger.info('| Finish parsing enemy...')

        return res_info

    async def _parse_map_text(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        parse 地图文本
        :param context_page:
        :param browser_context:
        :return:
        """

        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/251?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing map text...')
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
        res_info['id'] = 'map_text'
        res_info['name'] = 'map_text'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        map_text_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'map_text')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'map_text')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        map_texts_info = []
        for idx, map_text in enumerate(map_text_list):
            map_text = map_text.xpath('.//a')
            href = map_text.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = map_text.xpath('.//img/@data-src').extract_first()
            name = map_text.xpath('./@title').extract_first()

            map_text_parser = MapTextParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(map_text_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                map_texts_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            map_texts_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in map_texts_info})

        logger.info('| Finish parsing map text...')

        return res_info

    async def _parse_food(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/21?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing food...')
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
        res_info['id'] = 'food'
        res_info['name'] = 'food'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        food_list = selector.xpath('//a[@class="monster-image"]')

        img_dir = os.path.join(self.img_path, 'food')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'food')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        foods_info = []
        for idx, food in enumerate(food_list):
            href = food.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = food.xpath(
                './/div[@class="monster-image__top--image"]/img/@data-src'
            ).extract_first()
            name = food.xpath(
                './/div[@class="monster-image__top--title"]/text()'
            ).extract_first()

            food_parser = FoodParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(food_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                foods_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            foods_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in foods_info})

        logger.info('| Finish parsing food...')

        return res_info

    async def _parse_avatar(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/244?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing avatar...')

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
        res_info['id'] = 'avatar'
        res_info['name'] = 'avatar'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        avatar_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--avatar"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'avatar')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'avatar')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        avatars_info = []
        for idx, avatar in enumerate(avatar_list):
            avatar = avatar.xpath('.//a')
            href = avatar.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = avatar.xpath('.//img/@data-src').extract_first()
            name = avatar.xpath('./@title').extract_first()

            avatar_parser = AvatarParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(avatar_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                avatars_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            avatars_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in avatars_info})

        logger.info('| Finish parsing avatar...')

        return res_info

    async def _parse_backpack(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/13?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing backpack...')

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
        res_info['id'] = 'backpack'
        res_info['name'] = 'backpack'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        # ul.position-list__list.position-list__list--default
        backpack_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'backpack')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'backpack')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        backpacks_info = []

        for idx, backpack in enumerate(backpack_list):
            backpack = backpack.xpath('.//a')
            href = backpack.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = backpack.xpath('.//img/@data-src').extract_first()
            name = backpack.xpath('./@title').extract_first()

            backpack_parser = BackpackParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(backpack_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                backpacks_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            backpacks_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in backpacks_info})

        logger.info('| Finish parsing backpack...')

        return res_info

    async def _parse_activity(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/105?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing activity...')
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
        res_info['id'] = 'activity'
        res_info['name'] = 'activity'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        activity_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'activity')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'activity')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        activities_info = []
        for idx, activity in enumerate(activity_list):
            activity = activity.xpath('.//a')

            href = activity.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = activity.xpath('.//img/@data-src').extract_first()
            name = activity.xpath('./@title').extract_first()

            activity_parser = ActivityParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(activity_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                activities_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            activities_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in activities_info})

        logger.info('| Finish parsing activity...')

        return res_info

    async def _parse_task(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/43?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing task...')
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
        res_info['id'] = 'task'
        res_info['name'] = 'task'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        task_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'task')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'task')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        tasks_info = []
        for idx, task in enumerate(task_list):
            task = task.xpath('.//a')

            href = task.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = task.xpath('.//img/@data-src').extract_first()
            name = task.xpath('./@title').extract_first()

            task_parser = TaskParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(task_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                tasks_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            tasks_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in tasks_info})

        logger.info('| Finish parsing task...')

        return res_info

    async def _parse_animal(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/49?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing animal...')
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
        res_info['id'] = 'animal'
        res_info['name'] = 'animal'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        animal_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'animal')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'animal')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        animals_info = []
        for idx, animal in enumerate(animal_list):
            animal = animal.xpath('.//a')

            href = animal.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = animal.xpath('.//img/@data-src').extract_first()
            name = animal.xpath('./@title').extract_first()

            animal_parser = AnimalParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(animal_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                animals_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            animals_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in animals_info})

        logger.info('| Finish parsing animal...')

        return res_info

    async def _parse_book(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/68?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing book...')
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
        res_info['id'] = 'book'
        res_info['name'] = 'book'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        book_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'book')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'book')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        books_info = []
        for idx, book in enumerate(book_list):
            book = book.xpath('.//a')

            href = book.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = book.xpath('.//img/@data-src').extract_first()
            name = book.xpath('./@title').extract_first()

            book_parser = BookParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(book_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                books_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            books_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in books_info})

        logger.info('| Finish parsing book...')

        return res_info

    async def _parse_adventurer_guild(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/55?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing adventurer guild...')
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
        res_info['id'] = 'adventurer_guild'
        res_info['name'] = 'adventurer_guild'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        adventurer_guild_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'adventurer_guild')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'adventurer_guild')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        adventurer_guilds_info = []
        for idx, adventurer_guild in enumerate(adventurer_guild_list):
            adventurer_guild = adventurer_guild.xpath('.//a')

            href = adventurer_guild.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = adventurer_guild.xpath('.//img/@data-src').extract_first()
            name = adventurer_guild.xpath('./@title').extract_first()

            adventurer_guild_parser = AdventurerGuildParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(adventurer_guild_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                adventurer_guilds_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            adventurer_guilds_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in adventurer_guilds_info})

        logger.info('| Finish parsing adventurer guild...')

        return res_info

    async def _parse_npc(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/20?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing npc...')
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
        res_info['id'] = 'npc'
        res_info['name'] = 'npc'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        npc_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--avatar"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'npc')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'npc')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        npcs_info = []
        for idx, npc in enumerate(npc_list):
            npc = npc.xpath('.//a')

            href = npc.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = npc.xpath('.//img/@data-src').extract_first()
            name = npc.xpath('./@title').extract_first()

            npc_parser = NpcParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(npc_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                npcs_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            npcs_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in npcs_info})

        logger.info('| Finish parsing npc...')

        return res_info

    async def _parse_domain(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/54?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing domain...')
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
        res_info['id'] = 'domain'
        res_info['name'] = 'domain'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        domain_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'domain')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'domain')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        domains_info = []
        for idx, domain in enumerate(domain_list):
            domain = domain.xpath('.//a')

            href = domain.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = domain.xpath('.//img/@data-src').extract_first()
            name = domain.xpath('./@title').extract_first()

            domain_parser = DomainParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(domain_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                domains_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            domains_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in domains_info})

        logger.info('| Finish parsing domain...')

        return res_info

    async def _parse_fairyland(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/130?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing fairyland...')

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
        res_info['id'] = 'fairyland'
        res_info['name'] = 'fairyland'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        fairyland_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'fairyland')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'fairyland')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        fairylands_info = []
        for idx, fairyland in enumerate(fairyland_list):
            fairyland = fairyland.xpath('.//a')

            href = fairyland.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = fairyland.xpath('.//img/@data-src').extract_first()
            name = fairyland.xpath('./@title').extract_first()

            fairyland_parser = FairylandParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(fairyland_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                fairylands_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            fairylands_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in fairylands_info})

        logger.info('| Finish parsing fairyland...')

        return res_info

    async def _parse_abyss(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/65?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing abyss...')

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
        res_info['id'] = 'abyss'
        res_info['name'] = 'abyss'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        abyss_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'abyss')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'abyss')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        abysses_info = []
        for idx, abyss in enumerate(abyss_list):
            abyss = abyss.xpath('.//a')

            href = abyss.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = abyss.xpath('.//img/@data-src').extract_first()
            name = abyss.xpath('./@title').extract_first()

            abyss_parser = AbyssParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(abyss_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                abysses_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            abysses_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in abysses_info})

        logger.info('| Finish parsing abyss...')

        return res_info

    async def _parse_card(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/109?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing card...')
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
        res_info['id'] = 'card'
        res_info['name'] = 'card'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        # ul.position-list__list.position-list__list--default
        card_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'card')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'card')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        cards_info = []
        for idx, card in enumerate(card_list):
            card = card.xpath('.//a')

            href = card.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = card.xpath('.//img/@data-src').extract_first()
            name = card.xpath('./@title').extract_first()

            card_parser = CardParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(card_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                cards_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            cards_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in cards_info})

        logger.info('| Finish parsing card...')

        return res_info

    async def _parse_dress(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/211?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing dress...')
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
        res_info['id'] = 'dress'
        res_info['name'] = 'dress'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        # ul.position-list__list.position-list__list--default
        dress_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'dress')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'dress')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        dresses_info = []
        for idx, dress in enumerate(dress_list):
            dress = dress.xpath('.//a')

            href = dress.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = dress.xpath('.//img/@data-src').extract_first()
            name = dress.xpath('./@title').extract_first()

            dress_parser = DressParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(dress_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                dresses_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            dresses_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in dresses_info})

        logger.info('| Finish parsing dress...')

        return res_info

    async def _parse_tutorial(
        self, context_page: Page, browser_context: BrowserContext
    ) -> Dict[str, Any]:
        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/227?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing tutorial...')
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
        res_info: Dict[str, Any] = dict()
        res_info['url'] = self.url
        res_info['id'] = 'tutorial'
        res_info['name'] = 'tutorial'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        tutorial_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'tutorial')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'tutorial')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        tutorials_info = []
        for idx, tutorial in enumerate(tutorial_list):
            tutorial = tutorial.xpath('.//a')

            href = tutorial.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = tutorial.xpath('.//img/@data-src').extract_first()
            name = tutorial.xpath('./@title').extract_first()

            tutorial_parser = TutorialParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(tutorial_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                tutorials_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            tutorials_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in tutorials_info})

        logger.info('| Finish parsing tutorial...')

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

        res_info['敌人'] = await self._parse_enemy(context_page, browser_context)

        res_info['地图文本'] = await self._parse_map_text(context_page, browser_context)

        res_info['食物'] = await self._parse_food(context_page, browser_context)

        res_info['头像'] = await self._parse_avatar(context_page, browser_context)

        res_info['背包'] = await self._parse_backpack(context_page, browser_context)

        # TODO: 各个组件和元素未统一，暂时不详细解析，只解析了基础信息
        res_info['活动'] = await self._parse_activity(context_page, browser_context)

        res_info['任务'] = await self._parse_task(context_page, browser_context)

        res_info['动物'] = await self._parse_animal(context_page, browser_context)

        res_info['书籍'] = await self._parse_book(context_page, browser_context)

        res_info['冒险家协会'] = await self._parse_adventurer_guild(
            context_page, browser_context
        )

        res_info['NPC&商店'] = await self._parse_npc(context_page, browser_context)

        res_info['秘境'] = await self._parse_domain(context_page, browser_context)

        res_info['洞天'] = await self._parse_fairyland(context_page, browser_context)

        res_info['深境螺旋'] = await self._parse_abyss(context_page, browser_context)

        res_info['名片'] = await self._parse_card(context_page, browser_context)

        res_info['装扮'] = await self._parse_dress(context_page, browser_context)

        res_info['教程'] = await self._parse_tutorial(context_page, browser_context)

        # TODO: 各个组件和元素未统一，暂时不解析
        # 幻想真境剧诗

        return res_info
