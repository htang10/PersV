from collections import OrderedDict
from types import MappingProxyType
from typing import Generic

from src.pipeline.schemas import AgentT, CacheEntry, EngineT


class LRUCache(Generic[EngineT, AgentT]):
    def __init__(self, capacity: int) -> None:
        self.__cache: OrderedDict[str, CacheEntry[EngineT, AgentT]] = OrderedDict()
        self.__capacity = capacity

    def get_cache(self) -> MappingProxyType[str, CacheEntry[EngineT, AgentT]]:
        return MappingProxyType(self.__cache)

    def get(self, key: str) -> CacheEntry | None:
        if key not in self.__cache:
            return None
        self.__cache.move_to_end(key)
        return self.__cache.get(key)

    def put(
        self, key: str, cache_entry: CacheEntry[EngineT, AgentT]
    ) -> CacheEntry[EngineT, AgentT] | None:
        self.__cache[key] = cache_entry
        self.__cache.move_to_end(key)

        evicted = None
        if len(self.__cache) > self.__capacity:
            _, evicted = self.__cache.popitem(last=False)
        return evicted

    def pop(self, key: str) -> CacheEntry[EngineT, AgentT] | None:
        return self.__cache.pop(key) if key in self.__cache else None
