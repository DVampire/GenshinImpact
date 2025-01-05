import asyncio
import os
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.parser.character import CharacterParser
from crawler.utils.html_files import save_html_file
from crawler.utils.url import add_url

__all__ = [
    'IllustrationParser',
]


class IllustrationParser(AbstractParser):
    def __init__(self, config, url: str, page_name='wiki') -> None:
        self.config = config
        self.url = url
        self.page_name = page_name

    async def parse(
        self,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        parse page
        :param page:
        :return:
        """
        # New a context page
        context_page = await browser_context.new_page()

        logger.info(f'| Go to the page {self.url}')
        # Open the page
        await context_page.goto(self.url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        logger.info('| Start parsing page...')

        self.img_path = os.path.join(self.config.img_path, self.page_name)
        os.makedirs(self.img_path, exist_ok=True)
        self.html_path = os.path.join(self.config.html_path, self.page_name)
        os.makedirs(self.html_path, exist_ok=True)

        # Save a screenshot of the page
        # await self._save_screenshot(
        #     context_page,
        #     browser_context
        # )  # TODO: Comment it out for now, as this method causes the page to scroll, which slows down the speed.

        # Parse the page
        res_info = await self._parse(context_page, browser_context)

        logger.info('| Finish parsing page...')

        # Close the context page
        await context_page.close()

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

        # parse character
        res_info['角色'] = await self._parse_character(context_page, browser_context)

        return res_info

    async def _parse_character(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        """
        parse character (角色)
        :param page:
        :return: res_info: Dict[str, Any]
        """

        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/25?bbs_presentation_style=no_header&visit_device=pc'

        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing character...')

        img_path = os.path.join(self.img_path, 'character')
        os.makedirs(img_path, exist_ok=True)
        html_path = os.path.join(self.html_path, 'character')
        os.makedirs(html_path, exist_ok=True)

        # Save a screenshot of the page
        save_name = f'{0:04d}_full'
        # await scroll_and_capture(
        #     context_page, os.path.join(img_path, f'{save_name}.png')
        # ) # TODO: Comment it out for now, as this method causes the page to scroll, which slows down the speed.

        # Get the page content
        content = await context_page.content()

        # Save the HTML content to a file
        save_html_file(content, os.path.join(html_path, f'{save_name}.html'))

        # Get character list
        selector = Selector(text=content)

        character_list = selector.xpath('//a[@class="collection-avatar__item"]')

        tasks = []
        for idx, character in enumerate(character_list):
            href = character.xpath('./@href').extract_first()
            id = href.split(
                '/'
            )[
                4
            ]  # /ys/obc/content/503613/detail?bbs_presentation_style=no_header -> 503613
            href = add_url(href)
            icon = character.xpath(
                './div[@class="collection-avatar__icon"]/@data-src'
            ).extract_first()
            name = character.xpath(
                './div[@class="collection-avatar__title"]/text()'
            ).extract_first()

            character_parser = CharacterParser(
                config=self.config,
                url=href,
                page_name=id,
                character_name=name,
                icon=icon,
                img_path=img_path,
                html_path=html_path,
            )

            tasks.append(character_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == 1:
                await self._run_batch(tasks)
                tasks = []  # Reset tasks for the next batch

        if tasks:
            await self._run_batch(tasks)

        return res_info

    async def _run_batch(self, tasks):
        """
        Run a batch of tasks and handle any potential errors.
        """
        await asyncio.gather(*tasks)
