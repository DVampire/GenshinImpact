import asyncio
import os
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.parser.video_gallery_pages import (
    CharacterVideoParser,
    OtherVideoParser,
    TransitionAnimationParser,
)
from crawler.utils.url import add_url

__all__ = [
    'VideoGalleryParser',
]


class VideoGalleryParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'video_gallery',
        name: str = 'video_gallery',
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

    async def _parse_character_video(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/80/212?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing character video...')
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
        res_info['id'] = 'character_video'
        res_info['name'] = 'character_video'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        character_video_list = selector.xpath(
            '//ul[@class="summary-verti-list summary-verti-list--summaryVideo"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'character_video')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'character_video')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        character_videos_info = []
        for idx, character_video in enumerate(character_video_list):
            character_video = character_video.xpath('.//a')

            href = character_video.xpath('./@href').extract_first()
            id = href.split('/')[4]  # Extract the character ID from the URL
            href = add_url(href)

            icon = (
                character_video.xpath('.//div[@class="item__img"]/@data-src')
                .get()
                .strip()
            )

            name = (
                character_video.xpath('.//div[@class="item__info"]//text()')
                .get()
                .strip()
            )

            character_video_parser = CharacterVideoParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(character_video_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                character_videos_info.extend(await self._run_batch(tasks))
                tasks = []  # Reset tasks for the next batch

        if tasks:
            character_videos_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in character_videos_info})

        logger.info('| Finish parsing character video...')

        return res_info

    async def _parse_transition_animation(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/80/81?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing transition animation...')
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
        res_info['id'] = 'transition_animation'
        res_info['name'] = 'transition_animation'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        transition_animation_list = selector.xpath(
            '//ul[@class="summary-verti-list summary-verti-list--summaryVideo"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'transition_animation')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'transition_animation')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        transition_animations_info = []
        for idx, transition_animation in enumerate(transition_animation_list):
            transition_animation = transition_animation.xpath('.//a')

            href = transition_animation.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = (
                transition_animation.xpath('.//div[@class="item__img"]/@data-src')
                .get()
                .strip()
            )

            name = (
                transition_animation.xpath('.//div[@class="item__info"]//text()')
                .get()
                .strip()
            )

            transition_animation_parser = TransitionAnimationParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(transition_animation_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                transition_animations_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            transition_animations_info.extend(await self._run_batch(tasks))

        res_info['data'].update(
            {item['name']: item for item in transition_animations_info}
        )

        logger.info('| Finish parsing transition animation...')

        return res_info

    async def _parse_other_video(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/80/238?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing other video...')
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
        res_info['id'] = 'other_video'
        res_info['name'] = 'other_video'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        other_video_list = selector.xpath(
            '//ul[@class="summary-verti-list summary-verti-list--summaryVideo"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'other_video')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'other_video')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        other_videos_info = []
        for idx, other_video in enumerate(other_video_list):
            other_video = other_video.xpath('.//a')

            href = other_video.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = (
                other_video.xpath('.//div[@class="item__img"]/@data-src').get().strip()
            )

            name = (
                other_video.xpath('.//div[@class="item__info"]//text()').get().strip()
            )

            other_video_parser = OtherVideoParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(other_video_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                other_videos_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            other_videos_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in other_videos_info})

        logger.info('| Finish parsing other video...')

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

        res_info['角色视频'] = await self._parse_character_video(
            context_page, browser_context
        )

        res_info['过场动画'] = await self._parse_transition_animation(
            context_page, browser_context
        )

        res_info['其他视频'] = await self._parse_other_video(
            context_page, browser_context
        )

        return res_info
