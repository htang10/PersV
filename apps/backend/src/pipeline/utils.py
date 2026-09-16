from collections import OrderedDict
from types import MappingProxyType
from typing import Generic

from src.pipeline.schemas import AgentT, CacheEntry, EngineT


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

    def put(self, key: str, cache_entry: CacheEntry) -> CacheEntry | None:
        evicted = self.__cache.pop(key, None)
        self.__cache[key] = cache_entry  # automatically moved to the end

        if len(self.__cache) > self.__capacity:
            evicted = self.__cache.popitem(last=False)[-1]

        return evicted

    def pop(self, key: str) -> CacheEntry | None:
        return self.__cache.pop(key, None)
