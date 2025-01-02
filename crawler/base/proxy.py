from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

__all__ = ['ProviderNameEnum', 'IpInfoModel', 'ProxyProvider']


class ProviderNameEnum(Enum):
    KUAI_DAILI_PROVIDER: str = 'kuaidaili'


@dataclass
class IpInfoModel(BaseModel):
    ip: str = Field(title='ip')
    port: int = Field(title='host')
    user: str = Field(title='username')
    protocol: str = Field(default='https://', title='ip protocol')
    password: str = Field(title='password')
    expired_time_ts: Optional[int] = Field(title='expired time')


class ProxyProvider(ABC):
    @abstractmethod
    async def get_proxies(self, num: int) -> List[IpInfoModel]:
        """
        get ip abstract method
        :param num: number of ip
        :return:
        """
        raise NotImplementedError
