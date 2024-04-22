import logging
import time
from typing import Callable


def tracked(func: Callable):
    def wrapper(*args, **kwargs):
        st = time.perf_counter()
        rv = func(*args, **kwargs)
        et = time.perf_counter() - st
        print(f"--> {func.__qualname__}: {et}s")
        return rv
    return wrapper


class MistralLogger:
    def __init__(self, log_fullpath: str = None):
        if log_fullpath is None:
            log_fullpath = "/tmp/mistral.log"

        self.logger = logging.getLogger("MISTRAL")

        logging.basicConfig(filename=log_fullpath,
                            level=logging.INFO,
                            force=True)

    @staticmethod
    def __reformat(s: str) -> str:
        s = s.replace("\n", "")
        return (s[:61] + '...') if len(s) > 64 else s

    def __log(
            self, keyword: str,
            model: str,
            message: str,
            result: str,
            duration: float):

        head = f"[{keyword}, {model}, {int(duration * 1000)}ms]"
        body = f"['{self.__reformat(message)}', '{self.__reformat(result)}']"
        self.logger.info(f"{head}:{body}")

    def log_hit(self, model: str, message: str, result: str, duration: float):
        self.__log("HIT", model, message, result, duration)

    def log_miss(self, model: str, message: str, result: str, duration: float):
        self.__log("MISS", model, message, result, duration)
