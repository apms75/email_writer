import hashlib
import json
import os
from typing import Optional


class MistralCache:
    def __init__(self, dump_fullpath: str = None):
        if dump_fullpath is None:
            dump_fullpath = "/tmp/mistral_cache_dump.json"

        self.dump_fullpath = dump_fullpath

        if not os.path.exists(dump_fullpath):
            self.cache = {}
            return

        with open(dump_fullpath, mode="r") as fp:
            self.cache = json.loads(fp.read())

    @staticmethod
    def __get_hash(model: str, message: str) -> str:
        buf = model + message
        h = hashlib.sha512()
        h.update(buf.encode("utf-8"))
        return h.hexdigest()

    def __dump(self):
        with open(self.dump_fullpath, "w") as fp:
            json.dump(self.cache, fp)

    def try_get(self, model: str, message: str) -> Optional[str]:
        key = MistralCache.__get_hash(model, message)
        if key in self.cache:
            return self.cache[key][2]
        return None

    def add(self, model: str, message: str, answer: str):
        key = MistralCache.__get_hash(model, message)
        if key in self.cache:
            self.cache[key][2] = answer
        else:
            self.cache[key] = [model, message, answer]
        self.__dump()
