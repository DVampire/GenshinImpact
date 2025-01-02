import json
from typing import List

from crawler.base import IpInfoModel
from crawler.cache import LocalCache
from crawler.logger import logger


class IpCache:
    def __init__(self):
        self.cache_client = LocalCache(config=dict(cron_interval=10))

    def set_ip(self, ip_key: str, ip_value_info: str, ex: int):
        """
        set ip with expiration time, redis is responsible for deletion after expiration

        :param ip_key:
        :param ip_value_info:
        :param ex:
        :return:
        """
        self.cache_client.set(key=ip_key, value=ip_value_info, expire_time=ex)

    def load_all_ip(self, proxy_brand_name: str) -> List[IpInfoModel]:
        """
        load all IP information that has not expired from redis

        :param proxy_brand_name: proxy name
        :return:
        """
        all_ip_list: List[IpInfoModel] = []
        all_ip_keys: List[str] = self.cache_client.keys(pattern=f'{proxy_brand_name}_*')
        try:
            for ip_key in all_ip_keys:
                ip_value = self.cache_client.get(ip_key)
                if not ip_value:
                    continue
                all_ip_list.append(IpInfoModel(**json.loads(ip_value)))
        except Exception as e:
            logger.error('[IpCache.load_all_ip] get ip err from redis db', e)
        return all_ip_list
