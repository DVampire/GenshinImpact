import pickle
from typing import Any, Dict, List

from redis import Redis  # type: ignore

from crawler.base import AbstractCache


class RedisCache(AbstractCache):
    def __init__(self, *args, config: Dict[str, Any], **kwargs) -> None:
        """
        init redis cache

        :param config:
        """
        self.config = config

        self._redis_client = self._connet_redis()

    def _connet_redis(self) -> Redis:
        """
        connect to redis, and return redis client

        :return:
        """
        return Redis(
            host=self.config.get('redis_db_host'),
            port=self.config.get('redis_db_port'),
            db=self.config.get('redis_db_num'),
            password=self.config.get('redis_db_pwd'),
        )

    def get(self, key: str) -> Any:
        """
        get value from cache by key, and deserialize

        :param key:
        :return:
        """
        value = self._redis_client.get(key)
        if value is None:
            return None
        return pickle.loads(value)

    def set(self, key: str, value: Any, expire_time: int) -> None:
        """
        set value to cache by key, and serialize

        :param key:
        :param value:
        :param expire_time:
        :return:
        """
        self._redis_client.set(key, pickle.dumps(value), ex=expire_time)

    def keys(self, pattern: str) -> List[str]:
        """
        get all keys that match the pattern

        :param pattern:
        """
        return [key.decode() for key in self._redis_client.keys(pattern)]
