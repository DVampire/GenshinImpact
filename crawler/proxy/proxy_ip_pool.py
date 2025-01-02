import random
from typing import Dict, List

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from crawler.base import IpInfoModel, ProviderNameEnum, ProxyProvider
from crawler.logger import logger
from crawler.proxy.providers import create_kuai_daili_proxy


class ProxyIpPool:
    def __init__(
        self, ip_pool_count: int, enable_validate_ip: bool, ip_provider: ProxyProvider
    ) -> None:
        """
        init proxy ip pool

        :param ip_pool_count: ip pool count
        """
        self.valid_ip_url = 'https://httpbin.org/ip'  # valid ip url
        self.ip_pool_count = ip_pool_count
        self.enable_validate_ip = enable_validate_ip
        self.proxy_list: List[IpInfoModel] = []
        self.ip_provider: ProxyProvider = ip_provider

    async def load_proxies(self) -> None:
        """
        load proxies
        :return:
        """
        self.proxy_list = await self.ip_provider.get_proxies(self.ip_pool_count)

    async def _is_valid_proxy(self, proxy: IpInfoModel) -> bool:
        """
        test is valid proxy

        :param proxy:
        :return:
        """

        logger.info(f'[ProxyIpPool._is_valid_proxy] testing {proxy.ip} is it valid ')
        try:
            httpx_proxy = {
                f'{proxy.protocol}': f'http://{proxy.user}:{proxy.password}@{proxy.ip}:{proxy.port}'
            }
            async with httpx.AsyncClient(proxies=httpx_proxy) as client:
                response = await client.get(self.valid_ip_url)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            logger.info(f'[ProxyIpPool._is_valid_proxy] testing {proxy.ip} err: {e}')
            raise e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def get_proxy(self) -> IpInfoModel:
        """
        get an available proxy

        :return:
        """
        if len(self.proxy_list) == 0:
            await self._reload_proxies()

        proxy = random.choice(self.proxy_list)
        self.proxy_list.remove(proxy)  # remove the proxy from the list
        if self.enable_validate_ip:
            if not await self._is_valid_proxy(proxy):
                raise Exception(
                    '[ProxyIpPool.get_proxy] current ip invalid and again get it'
                )
        return proxy

    async def _reload_proxies(self):
        """
        # reload proxies
        :return:
        """
        self.proxy_list = []
        await self.load_proxies()


IpProxyProvider: Dict[str, ProxyProvider] = {
    ProviderNameEnum.KUAI_DAILI_PROVIDER.value: create_kuai_daili_proxy()
}


async def create_ip_pool(ip_pool_count: int, enable_validate_ip: bool) -> ProxyIpPool:
    """
    create ip pool
    :param ip_pool_count: ip pool count
    :param enable_validate_ip: if enable validate ip
    :return:
    """
    pool = ProxyIpPool(
        ip_pool_count=ip_pool_count,
        enable_validate_ip=enable_validate_ip,
        ip_provider=IpProxyProvider[ProviderNameEnum.KUAI_DAILI_PROVIDER.value],
    )
    await pool.load_proxies()
    return pool
