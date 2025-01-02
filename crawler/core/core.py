import os
from typing import Dict, Optional, Tuple

from playwright.async_api import BrowserContext, BrowserType, Page, async_playwright

from crawler.base import AbstractCrawler, IpInfoModel
from crawler.core.client import Client
from crawler.logger import logger
from crawler.proxy import create_ip_pool
from crawler.utils.file_utils import assemble_project_path
from crawler.utils.html_files import save_html_file
from crawler.utils.screenshot import scroll_and_capture


class Crawler(AbstractCrawler):
    context_page: Page
    xhs_client: Client
    browser_context: BrowserContext

    def __init__(
        self,
        *args,
        config,
        **kwargs,
    ) -> None:
        self.config = config
        self.index_url = 'https://bbs.mihoyo.com/ys/obc/?bbs_presentation_style=no_header&visit_device=pc'
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
            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url)

            # Ensure all network activity is complete
            await self.context_page.wait_for_load_state('networkidle')
            await self.context_page.wait_for_selector('div[class="calendar"]')

            # Save a screenshot of the page
            await scroll_and_capture(self.context_page, 'index.png')

            # Get the page content
            content = await self.context_page.content()

            # Save the HTML content to a file
            save_html_file(content, 'index.html')

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """Launch browser and create browser context"""
        logger.info('Begin create browser context ...')
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
                headless=headless, proxy=playwright_proxy, java_script_enabled=True
            )  # type: ignore
            browser_context = await browser.new_context(user_agent=user_agent)
            return browser_context

    async def search(self):
        pass
