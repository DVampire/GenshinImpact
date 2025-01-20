import asyncio
import os
from typing import Any, Dict, Optional

from playwright.async_api import BrowserContext, Page
from scrapy.selector import Selector

from crawler.base import AbstractParser
from crawler.logger import logger
from crawler.parser.wiki_pages.observation_pages import (
    MethodologyParser,
    RegionParser,
)
from crawler.utils.url import add_url

__all__ = [
    'ObservationParser',
]


class ObservationParser(AbstractParser):
    def __init__(
        self,
        *args,
        config,
        url: str,
        img_path: str,
        html_path: str,
        id: str = 'observation',
        name: str = 'observation',
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

    async def _parse_region(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/190/7?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing region...')
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
        res_info['id'] = 'region'
        res_info['name'] = 'region'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        region_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--card"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'region')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'region')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        regions_info = []
        for idx, region in enumerate(region_list):
            region = region.xpath('.//a')

            href = region.xpath('./@href').extract_first()
            id = href.split('/')[4]  # Extract the character ID from the URL
            href = add_url(href)

            icon = region.xpath('.//img/@data-src').extract_first()

            name = region.xpath('./@title').extract_first()

            region_parser = RegionParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(region_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                regions_info.extend(await self._run_batch(tasks))
                tasks = []  # Reset tasks for the next batch

        if tasks:
            regions_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in regions_info})

        logger.info('| Finish parsing region...')

        return res_info

    async def _parse_methodology(
        self,
        context_page: Optional[Page] = None,
        browser_context: Optional[BrowserContext] = None,
    ) -> Dict[str, Any]:
        res_info: Dict[str, Any] = dict()

        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/190/62?bbs_presentation_style=no_header&visit_device=pc'

        logger.info(f'| Go to the page {url}')
        # Open the page
        await context_page.goto(url)

        # Ensure all network activity is complete
        await context_page.wait_for_load_state('networkidle')

        # start parsing
        logger.info('| Start parsing methodology...')
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
        res_info['id'] = 'methodology'
        res_info['name'] = 'methodology'
        res_info['img_path'] = img_path
        res_info['html_path'] = html_path
        res_info['data']: Dict[str, Any] = dict()

        selector = Selector(text=content)

        methodology_list = selector.xpath(
            '//ul[@class="position-list__list position-list__list--default"]'
        ).xpath('.//li')

        img_dir = os.path.join(self.img_path, 'methodology')
        os.makedirs(img_dir, exist_ok=True)
        html_dir = os.path.join(self.html_path, 'methodology')
        os.makedirs(html_dir, exist_ok=True)

        tasks = []
        methdologies_info = []
        for idx, methodology in enumerate(methodology_list):
            methodology = methodology.xpath('.//a')

            href = methodology.xpath('./@href').extract_first()
            id = href.split('/')[4]

            href = add_url(href)

            icon = methodology.xpath('.//img/@data-src').extract_first()

            name = methodology.xpath('./@title').extract_first()

            methodology_parser = MethodologyParser(
                config=self.config,
                url=href,
                id=id,
                name=name,
                icon=icon,
                img_path=img_dir,
                html_path=html_dir,
            )

            tasks.append(methodology_parser.parse(browser_context))

            # If batch size is reached, execute the tasks
            if len(tasks) == self.config.batch_size:
                methdologies_info.extend(await self._run_batch(tasks))
                tasks = []

        if tasks:
            methdologies_info.extend(await self._run_batch(tasks))

        res_info['data'].update({item['name']: item for item in methdologies_info})

        logger.info('| Finish parsing methodology...')

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

        res_info['区域'] = await self._parse_region(context_page, browser_context)

        res_info['考据'] = await self._parse_methodology(context_page, browser_context)

        return res_info
