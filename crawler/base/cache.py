from abc import ABC, abstractmethod
from typing import List, Optional

__all__ = ['AbstractCache']


class AbstractCache(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """
        get key
        :param key:
        :return:
        """
        pass

    @abstractmethod
    def set(self, key: str, value: str, expire_time: int):
        """
        set key
        :param key:
        :param value:
        :param expire_time:
        :return:
        """
        pass

    @abstractmethod
    def keys(self, pattern: str) -> List:
        """
        get keys
        :param pattern:
        :return:
        """
        pass
