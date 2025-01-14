import os
from typing import Dict, Optional, Tuple

from playwright.async_api import BrowserContext, BrowserType, async_playwright

from crawler.base import AbstractCrawler, IpInfoModel
from crawler.logger import logger
from crawler.parser.illustration import IllustrationParser
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

    async def search(self):
        # wiki (观测 Wiki)
        # url = 'https://bbs.mihoyo.com/ys/obc/?bbs_presentation_style=no_header&visit_device=pc'
        # wiki_parser = WikiParser(config=self.config,
        #                          url=url,
        #                          id='wiki',
        #                          name='wiki',
        #                          img_path=self.config.img_path,
        #                          html_path=self.config.html_path,
        #                          )
        # wiki_res_info = await wiki_parser.parse(self.browser_context)
        # logger.info(f'Wiki: {wiki_res_info}')
        #
        # # strategy (观测 攻略)
        # url = 'https://bbs.mihoyo.com/ys/strategy/?bbs_presentation_style=no_header'
        # strategy_parser = StrategyParser(config=self.config,
        #                                  url=url,
        #                                  id='strategy',
        #                                  name='strategy',
        #                                  img_path=self.config.img_path,
        #                                  html_path=self.config.html_path,
        #                                  )
        # strategy_res_info = await strategy_parser.parse(self.browser_context)
        # logger.info(f'Strategy: {strategy_res_info}')
        #
        # # summon (观测 七圣召唤)
        # url = 'https://bbs.mihoyo.com/ys/strategy/summon?bbs_presentation_style=no_header'
        # summon_parser = SummonParser(config=self.config,
        #                              url=url,
        #                              id='summon',
        #                              name='summon',
        #                              img_path=self.config.img_path,
        #                              html_path=self.config.html_path,
        #                              )
        # summon_res_info = await summon_parser.parse(self.browser_context)
        # logger.info(f'Summon: {summon_res_info}')

        # illustration (首页 图鉴)
        url = 'https://bbs.mihoyo.com/ys/obc/channel/map/189/25?bbs_presentation_style=no_header&visit_device=pc'
        illustration_parser = IllustrationParser(
            config=self.config,
            url=url,
            id='illustration',
            name='illustration',
            img_path=self.config.img_path,
            html_path=self.config.html_path,
        )
        illustration_res_info = await illustration_parser.parse(self.browser_context)
        logger.info(f'Illustration: {illustration_res_info}')
