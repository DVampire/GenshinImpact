import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple

from crawler.base import AbstractCache

__all__ = ['LocalCache']


class LocalCache(AbstractCache):
    def __init__(self, *args, config: Dict[str, Any], **kwargs) -> None:
        """
        init local cache

        :param config: config for local cache
        :return:
        """
        self.config = config
        self._cron_interval = config.get('cron_interval', 10)
        self._cache_container: Dict[str, Tuple[Any, float]] = {}
        self._cron_task: Optional[asyncio.Task] = None
        self._schedule_clear()

    def __del__(self):
        """
        destructor, clear the cron task
        :return:
        """
        if self._cron_task is not None:
            self._cron_task.cancel()

    def get(self, key: str) -> Optional[Any]:
        """
        get value from cache by key

        :param key:
        :return:
        """
        value, expire_time = self._cache_container.get(key, (None, 0))
        if value is None:
            return None

        # if the key has expired, delete the key and return None
        if expire_time < time.time():
            del self._cache_container[key]
            return None

        return value

    def set(self, key: str, value: Any, expire_time: int) -> None:
        """
        set value to cache by key

        :param key:
        :param value:
        :param expire_time:
        :return:
        """
        self._cache_container[key] = (value, time.time() + expire_time)

    def keys(self, pattern: str) -> List[str]:
        """
        get all keys that match the pattern

        :param pattern: match pattern
        :return:
        """
        if pattern == '*':
            return list(self._cache_container.keys())

        # replace * with empty string
        if '*' in pattern:
            pattern = pattern.replace('*', '')

        return [key for key in self._cache_container.keys() if pattern in key]

    def _schedule_clear(self):
        """
        start the cron task for clearing cache
        :return:
        """

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._cron_task = loop.create_task(self._start_clear_cron())

    def _clear(self):
        """
        clear cache based on expiration time
        :return:
        """
        for key, (value, expire_time) in self._cache_container.items():
            if expire_time < time.time():
                del self._cache_container[key]

    async def _start_clear_cron(self):
        """
        start the cron task for clearing cache
        :return:
        """
        while True:
            self._clear()
            await asyncio.sleep(self._cron_interval)
