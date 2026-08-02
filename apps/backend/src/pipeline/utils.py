from collections import OrderedDict
from types import MappingProxyType
from typing import TypeAlias

from sqlalchemy import Engine

EngineCache: TypeAlias = dict[str, Engine]


class LRUEngineCache:
    def __init__(self, capacity: int) -> None:
        self.__cache = OrderedDict()
        self.__capacity = capacity

    def get_cache(self) -> MappingProxyType[str, Engine]:
        """Returns a read-only snapshot of the current engine cache.

        Returns:
            A read-only mapping of user IDs to their cached SQLAlchemy engines.
        """
        return MappingProxyType(self.__cache)

    def get(self, key: str) -> EngineCache | None:
        if key not in self.__cache:
            return None
        self.__cache.move_to_end(key)
        return self.__cache.get(key)

    def put(self, key: str, target: str, engine: Engine | None) -> None:
        if engine:  # CUSTOM
            self.__cache[key] = {
                "target": target,
                "engine": engine,
            }
        else:  # DEMO
            self.__cache[key] = {
                "target": target,
            }
        self.__cache.move_to_end(key)
        if len(self.__cache) > self.__capacity:
            self.__cache.popitem(last=False)

    def pop(self, key: str) -> EngineCache | None:
        return self.__cache.pop(key) if key in self.__cache else None
