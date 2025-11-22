from collections import OrderedDict
from typing import Optional

class LRUCache:
    def __init__(self, capacity: int, max_size: int):
        self.capacity = capacity
        self.max_size = max_size
        self._store: OrderedDict[str, bytes] = OrderedDict()

    def get(self, key: str) -> Optional[bytes]:
        if key in self._store:
            self._store.move_to_end(key)
            return self._store[key]
        return None

    def put(self, key: str, value: bytes):
        if len(value) > self.max_size:
            return
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self.capacity:
            self._store.popitem(last=False)
