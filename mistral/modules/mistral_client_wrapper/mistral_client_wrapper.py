from enum import Enum
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import time

from mistral_cache import MistralCache
from mistral_logger import MistralLogger


class MistralModel(str, Enum):
    LARGE = "mistral-large-latest"
    SMALL = "mistral-small"
    OPEN7B = "open-mistral-7b"
    EMBED = "mistral-embed"


class MistralClientWrapper:
    def __init__(
            self, api_key: str,
            model: MistralModel,
            logger: MistralLogger,
            cache: MistralCache):

        self.api_key = api_key
        self.model = model
        self.logger = logger
        self.cache = cache

        self.client = MistralClient(api_key=api_key)

    def __try_get(self, message: str) -> str:
        return self.cache.try_get(self.model, message)

    def __chat(self, user_message: str, system_message: str) -> str:
        messages = []
        if system_message is not None:
            messages.append(ChatMessage(role="system", content=system_message))
        messages.append(ChatMessage(role="user", content=user_message))

        chat_response = self.client.chat(model=self.model.value,
                                         messages=messages)

        return chat_response.choices[0].message.content

    def chat(self, user_message: str, system_message=None) -> str:
        st = time.perf_counter()

        msg = user_message + str(system_message or "")
        res = self.__try_get(msg)
        if res is not None:
            self.logger.log_hit(self.model, msg, res, time.perf_counter() - st)
            return res

        res = self.__chat(user_message, system_message)
        self.cache.add(self.model, msg, res)

        self.logger.log_miss(self.model, msg, res, time.perf_counter() - st)
        return res
