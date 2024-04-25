from collections import Counter
from dotenv import load_dotenv
import json
import os
from typing import Callable, List, Optional

import __mistral_wrapper__
from mistral_cache import MistralCache
from mistral_logger import MistralLogger
from mistral_client_wrapper import MistralClientWrapper
from mistral_client_wrapper import MistralModel

import messages as msg


input_filepath = "emails-clean.json"
output_filepath = "emails-final.json"


def load_json() -> List[object]:
    with open(input_filepath, mode="r") as fp:
        r = fp.read()
        arr = json.loads(r)
        return arr


def dump_json(arr: List[object]):
    with open(output_filepath, "w") as fp:
        json.dump(arr, fp)


def open_mistral_client() -> MistralClientWrapper:
    load_dotenv()
    return MistralClientWrapper(
        os.environ["MISTRAL_API_KEY"],
        MistralModel.LARGE,
        MistralLogger(os.environ["MISTRAL_LOGGING_FILE"]),
        MistralCache(os.environ["MISTRAL_CACHE_DUMP"]))


def insert_attribute(
        pairs: List[object],
        keyword: str,
        list: List[object]) -> List[object]:

    for i, l in enumerate(list):
        pairs[i][keyword] = l


def display_attribute(emails: List[object], keyword: str):
    for i, email in enumerate(emails):
        print("=" * 80)
        print(f"{i + 1}. {email[keyword]}")


def message_printf(msg: str, values: List[object]) -> str:
    for v in values:
        msg = msg.replace(v[0], v[1])
    return msg


def generate_list(
        pairs: List[object],
        client: MistralClientWrapper,
        func: Callable) -> List[str]:

    res = [""] * len(pairs)
    for i, pair in enumerate(pairs):
        res[i] = func(pair, client)
    return res


def generate_one_email(pair: object, client: MistralClientWrapper) -> str:
    user_msg = message_printf(msg.user_message_email, [
        ("[sender]", pair["recipient_name"]),
        ("[recipient]", pair["sender_name"]),
        ("[relationship]", pair["relationship"] or "des connaissances"),
        ("[example]", pair["body"]),
        ("[message]", msg.email_template)])

    return client.chat(user_msg)


def generate_emails(pairs: List[object],
                    client: MistralClientWrapper) -> List[str]:

    return generate_list(pairs, client, generate_one_email)


def main():
    sender_recipient_pairs = list(filter(
        lambda x: x["sender_name"] and x["recipient_name"], load_json()))

    emails = generate_emails(sender_recipient_pairs, open_mistral_client())
    insert_attribute(sender_recipient_pairs, "email", emails)

    dump_json(sender_recipient_pairs)

    display_attribute(sender_recipient_pairs, "email")


if __name__ == "__main__":
    main()
