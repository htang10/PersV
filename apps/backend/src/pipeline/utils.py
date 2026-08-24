from collections import OrderedDict
from types import MappingProxyType
from typing import Generic, TypedDict, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class CacheEntry[T, U](TypedDict):
    target: str
    engine: T | None
    agent: U | None


class LRUCache(Generic[T, U]):
    def __init__(self, capacity: int) -> None:
        self.__cache: OrderedDict[str, CacheEntry[T, U]] = OrderedDict()
        self.__capacity = capacity

    def get_cache(self) -> MappingProxyType[str, CacheEntry[T, U]]:
        return MappingProxyType(self.__cache)

    def get(self, key: str) -> CacheEntry | None:
        if key not in self.__cache:
            return None
        self.__cache.move_to_end(key)
        return self.__cache.get(key)

    def put(
        self, key: str, target: str, engine: T | None, agent: U | None
    ) -> CacheEntry[T, U] | None:
        self.__cache[key] = {
            "target": target,
            "engine": engine,
            "agent": agent,
        }
        self.__cache.move_to_end(key)

        evicted = None
        if len(self.__cache) > self.__capacity:
            _, evicted = self.__cache.popitem(last=False)
        return evicted

    def pop(self, key: str) -> CacheEntry[T, U] | None:
        return self.__cache.pop(key) if key in self.__cache else None
