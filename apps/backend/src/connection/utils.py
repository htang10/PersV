from collections import OrderedDict
from types import MappingProxyType
from typing import Generic

from fastapi import Request

from src.connection.schemas import AgentT, CacheEntry, EngineT


def get_client_ip(request: Request) -> str:
    return request.headers.get("x-real-ip") or request.client.host or "unknown"


class LRUCache(Generic[EngineT, AgentT]):
    def __init__(self, capacity: int) -> None:
        self.__cache: OrderedDict[str, CacheEntry[EngineT, AgentT]] = OrderedDict()
        self.__capacity = capacity

    def get_cache(self) -> MappingProxyType[str, CacheEntry]:
        return MappingProxyType(self.__cache)

    def get(self, key: str) -> CacheEntry | None:
        entry = self.__cache.get(key)
        if entry is not None:
            self.__cache.move_to_end(key)
        return entry

    def put(self, key: str, cache_entry: CacheEntry) -> list[CacheEntry]:
        """Inserts an entry and returns every entry that was removed to make room."""
        removed = []
        if (replaced := self.__cache.pop(key, None)) is not None:
            removed.append(replaced)
        self.__cache[key] = cache_entry

        while len(self.__cache) > self.__capacity:
            removed.append(self.__cache.popitem(last=False)[1])
        return removed

    def pop(self, key: str) -> CacheEntry | None:
        return self.__cache.pop(key, None)
