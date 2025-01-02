import os
import re
from dataclasses import dataclass
from typing import Dict, List

import httpx
from pydantic import BaseModel, Field

from crawler.base import IpInfoModel, ProviderNameEnum, ProxyProvider
from crawler.logger import logger
from crawler.proxy.ip_cache import IpCache


@dataclass
class KuaidailiProxyModel(BaseModel):
    ip: str = Field('ip')
    port: int = Field('host')
    expire_ts: int = Field('expired time')


def parse_kuaidaili_proxy(proxy_info: str) -> KuaidailiProxyModel:
    """
    parse kuaidaili ip info

    :param proxy_info:
    """
    proxies: List[str] = proxy_info.split(':')
    if len(proxies) != 2:
        raise Exception('not invalid kuaidaili proxy info')

    pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5}),(\d+)'

    match = re.search(pattern, proxy_info)

    if not match:
        raise Exception('not match kuaidaili proxy info')

    return KuaidailiProxyModel(
        ip=match.groups()[0],
        port=int(match.groups()[1]),
        expire_ts=int(match.groups()[2]),
    )


class KuaiDaiLiProxy(ProxyProvider):
    def __init__(
        self,
        kdl_user_name: str,
        kdl_user_pwd: str,
        kdl_secret_id: str,
        kdl_signature: str,
    ):
        """

        Args:
            kdl_user_name:
            kdl_user_pwd:
        """
        self.kdl_user_name = kdl_user_name
        self.kdl_user_pwd = kdl_user_pwd
        self.api_base = 'https://dps.kdlapi.com/'
        self.secret_id = kdl_secret_id
        self.signature = kdl_signature
        self.ip_cache = IpCache()
        self.proxy_brand_name = ProviderNameEnum.KUAI_DAILI_PROVIDER.value
        self.params = {
            'secret_id': self.secret_id,
            'signature': self.signature,
            'pt': 1,
            'format': 'json',
            'sep': 1,
            'f_et': 1,
        }

    async def get_proxies(self, num: int) -> List[IpInfoModel]:
        """
        implement kuaidaili proxy

        :param num: number of ip
        """
        uri = '/api/getdps/'

        # get ip from cache
        ip_cache_list = self.ip_cache.load_all_ip(
            proxy_brand_name=self.proxy_brand_name
        )
        if len(ip_cache_list) >= num:
            return ip_cache_list[:num]

        # if cache ip not enough, get from provider
        need_get_count = num - len(ip_cache_list)
        self.params.update({'num': need_get_count})

        ip_infos: List[IpInfoModel] = []
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_base + uri, params=self.params)

            if response.status_code != 200:
                logger.error(
                    f'[KuaiDaiLiProxy.get_proxies] statuc code not 200 and response.txt:{response.text}'
                )
                raise Exception(
                    'get ip error from proxy provider and status code not 200 ...'
                )

            ip_response: Dict = response.json()
            if ip_response.get('code') != 0:
                logger.error(
                    f'[KuaiDaiLiProxy.get_proxies]  code not 0 and msg:{ip_response.get('msg')}'
                )
                raise Exception('get ip error from proxy provider and  code not 0 ...')

            proxy_list: List[str] = ip_response.get('data', {}).get('proxy_list')
            for proxy in proxy_list:
                proxy_model = parse_kuaidaili_proxy(proxy)
                ip_info_model = IpInfoModel(
                    ip=proxy_model.ip,
                    port=proxy_model.port,
                    user=self.kdl_user_name,
                    password=self.kdl_user_pwd,
                    expired_time_ts=proxy_model.expire_ts,
                )
                ip_key = (
                    f'{self.proxy_brand_name}_{ip_info_model.ip}_{ip_info_model.port}'
                )
                self.ip_cache.set_ip(
                    ip_key,
                    ip_info_model.model_dump_json(),
                    ex=ip_info_model.expired_time_ts,
                )
                ip_infos.append(ip_info_model)

        return ip_cache_list + ip_infos


def create_kuai_daili_proxy() -> KuaiDaiLiProxy:
    """
    create kuaidaili proxy

    :return:
    """
    return KuaiDaiLiProxy(
        kdl_secret_id=os.getenv('kdl_secret_id', 'secert_id'),
        kdl_signature=os.getenv('kdl_signature', 'signature'),
        kdl_user_name=os.getenv('kdl_username', 'username'),
        kdl_user_pwd=os.getenv('kdl_password', 'password'),
    )
