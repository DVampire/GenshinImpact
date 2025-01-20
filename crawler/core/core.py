import os
from typing import Any, Dict, Optional, Tuple

from playwright.async_api import BrowserContext, BrowserType, async_playwright

from crawler.base import AbstractCrawler, IpInfoModel
from crawler.logger import logger
from crawler.parser.strategy import StrategyParser
from crawler.parser.summon import SummonParser
from crawler.parser.wiki_pages.card import CardParser
from crawler.parser.wiki_pages.illustration import IllustrationParser
from crawler.parser.wiki_pages.observation import ObservationParser
from crawler.parser.wiki_pages.video_gallery import VideoGalleryParser
from crawler.proxy import create_ip_pool
from crawler.utils.file_utils import assemble_project_path


class Crawler(AbstractCrawler):
    browser_context: BrowserContext

    def __init__(
        self,
        *args,
        config,
        **kwargs,
    ) -> None:
        self.config = config
        self.user_agent = (
            config.user_agent
            if config.user_agent
            else 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        )

    @staticmethod
    def format_proxy_info(
        ip_proxy_info: IpInfoModel,
    ) -> Tuple[Optional[Dict], Optional[Dict]]:
        """format proxy info for playwright and httpx"""
        playwright_proxy = {
            'server': f'{ip_proxy_info.protocol}{ip_proxy_info.ip}:{ip_proxy_info.port}',
            'username': ip_proxy_info.user,
            'password': ip_proxy_info.password,
        }
        httpx_proxy = {
            f'{ip_proxy_info.protocol}': f'http://{ip_proxy_info.user}:{ip_proxy_info.password}@{ip_proxy_info.ip}:{ip_proxy_info.port}'
        }
        return playwright_proxy, httpx_proxy

    async def start(self):
        playwright_proxy_format, httpx_proxy_format = None, None
        if self.config.enable_ip_proxy:
            ip_proxy_pool = await create_ip_pool(
                self.config.ip_proxy_pool_count, enable_validate_ip=True
            )
            ip_proxy_info: IpInfoModel = await ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = self.format_proxy_info(
                ip_proxy_info
            )

        async with async_playwright() as playwright:
            # Launch a browser context.
            chromium = playwright.chromium
            self.browser_context = await self.launch_browser(
                chromium, None, self.user_agent, headless=self.config.headless
            )
            # stealth.min.js is a js script to prevent the website from detecting the crawler.
            await self.browser_context.add_init_script(
                path=assemble_project_path('libs/stealth.min.js')
            )
            # add a cookie attribute webId to avoid the appearance of a sliding captcha on the webpage
            await self.browser_context.add_cookies(
                [
                    {
                        'name': 'webId',
                        'value': 'xxx123',  # any value
                        'domain': '.mihoyo.com',
                        'path': '/',
                    }
                ]
            )

            await self.search()

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """Launch browser and create browser context"""
        logger.info('| Begin create browser context ...')
        if self.config.save_login_state:
            # feat issue #14

            # we will save login state to avoid login every time
            user_data_dir = str(
                os.path.join(self.config.exp_path, self.config.user_data_dir)
            )

            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=headless,
                proxy=playwright_proxy,  # type: ignore
                user_agent=user_agent,
                java_script_enabled=True,
            )
            return browser_context
        else:
            browser = await chromium.launch(
                headless=headless,
                proxy=playwright_proxy,
            )  # type: ignore
            browser_context = await browser.new_context(user_agent=user_agent)
            return browser_context

    async def _parse_wiki(self):
        res_info: Dict[str, Any] = {}

        # # wiki (观测 Wiki)
        # url = 'https://bbs.mihoyo.com/ys/obc/?bbs_presentation_style=no_header&visit_device=pc'
        # wiki_parser = WikiParser(
        #     config=self.config,
        #     url=url,
        #     id='wiki',
        #     name='wiki',
        #     img_path=self.config.img_path,
        #     html_path=self.config.html_path,
        # )
        # wiki_res_info = await wiki_parser.parse(self.browser_context)
        # logger.info(f'Wiki: {wiki_res_info}')
        # res_info.update(wiki_res_info)

        # wiki pages
        # illustration (首页 图鉴)
        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/25?bbs_presentation_style=no_header&visit_device=pc'
        illustration_parser = IllustrationParser(
            config=self.config,
            url=url,
            id='illustration',
            name='illustration',
            icon=None,
            img_path=self.config.img_path,
            html_path=self.config.html_path,
        )
        illustration_res_info = await illustration_parser.parse(self.browser_context)
        logger.info(f'Illustration: {illustration_res_info}')

        # 卡牌图鉴 (卡牌图鉴)
        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/231/233?bbs_presentation_style=no_header&visit_device=pc'
        card_parser = CardParser(
            config=self.config,
            url=url,
            id='card',
            name='card',
            icon=None,
            img_path=self.config.img_path,
            html_path=self.config.html_path,
        )
        card_res_info = await card_parser.parse(self.browser_context)
        logger.info(f'Card: {card_res_info}')

        # 观测 影音回廊
        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/80/212?bbs_presentation_style=no_header&visit_device=pc'
        video_gallery_parser = VideoGalleryParser(
            config=self.config,
            url=url,
            id='video_gallery',
            name='video_gallery',
            icon=None,
            img_path=self.config.img_path,
            html_path=self.config.html_path,
        )
        video_gallery_res_info = await video_gallery_parser.parse(self.browser_context)
        logger.info(f'VideoGallery: {video_gallery_res_info}')

        # 观测
        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/190/7?bbs_presentation_style=no_header&visit_device=pc'
        observation_parser = ObservationParser(
            config=self.config,
            url=url,
            id='observation',
            name='observation',
            icon=None,
            img_path=self.config.img_path,
            html_path=self.config.html_path,
        )
        observation_res_info = await observation_parser.parse(self.browser_context)
        logger.info(f'Observation: {observation_res_info}')

        res_info.update(illustration_res_info)
        res_info.update(card_res_info)
        res_info.update(video_gallery_res_info)
        res_info.update(observation_res_info)

        return res_info

    async def _parse_strategy(self):
        res_info: Dict[str, Any] = {}

        # strategy (观测 攻略)
        url = 'https://bbs.mihoyo.com/ys/strategy/?bbs_presentation_style=no_header'
        strategy_parser = StrategyParser(
            config=self.config,
            url=url,
            id='strategy',
            name='strategy',
            icon=None,
            img_path=self.config.img_path,
            html_path=self.config.html_path,
        )
        strategy_res_info = await strategy_parser.parse(self.browser_context)
        logger.info(f'Strategy: {strategy_res_info}')

        res_info.update(strategy_res_info)

        return res_info

    async def _parse_summon(self):
        res_info: Dict[str, Any] = {}

        # summon (观测 七圣召唤)
        url = (
            'https://bbs.mihoyo.com/ys/strategy/summon?bbs_presentation_style=no_header'
        )
        summon_parser = SummonParser(
            config=self.config,
            url=url,
            id='summon',
            name='summon',
            icon=None,
            img_path=self.config.img_path,
            html_path=self.config.html_path,
        )
        summon_res_info = await summon_parser.parse(self.browser_context)
        logger.info(f'Summon: {summon_res_info}')

        res_info.update(summon_res_info)

        return res_info

    async def search(self):
        # wiki
        wiki_res_info = await self._parse_wiki()
        logger.info(f'Wiki: {wiki_res_info}')

        # # strategy
        # strategy_res_info = await self._parse_strategy()
        #
        # # summon
        # summon_res_info = await self._parse_summon()
