from dotenv import load_dotenv
import json
import os
import re
from typing import List

import __mistral_wrapper__
from mistral_cache import MistralCache
from mistral_logger import MistralLogger
from mistral_client_wrapper import MistralClientWrapper
from mistral_client_wrapper import MistralModel

import messages as msg


input_filepath = "emails-clean.json"
output_filepath = "emails-screening.json"


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
        MistralCache(os.environ["MISTRAL_CACHE_DUMP"])
    )


def display_distinct_bodies(pairs: List[object]):
    bodies = set()
    for pair in pairs:
        for body in pair["bodies"]:
            bodies.add(body)

    for i, body in enumerate(bodies):
        print("=" * 80)
        print(f"{i + 1}. {body}")


def is_positive_answer(answer):
    exp = r"\b({0})\b".format("Oui")
    return re.compile(exp, flags=re.IGNORECASE).search(answer[:80])


def is_written_by_close_family(
        body: str,
        client: MistralClientWrapper) -> bool:

    buf = client.chat(
        msg.system_message_yes_no_multiple,
        msg.user_message_family_1 + body)
    if is_positive_answer(buf):
        return True

    buf = client.chat(
        msg.system_message_yes_no_multiple,
        msg.user_message_family_2 + body)
    if is_positive_answer(buf):
        return True

    return False


def screen_out_close_family(
        pairs: List[object],
        client: MistralClientWrapper) -> List[object]:

    res = []
    for pair in pairs:
        for body in pair["bodies"]:
            if is_written_by_close_family(body, client):
                break
        else:
            res.append(pair)
    return res


def is_written_by_friend_and_business(
        body: str,
        client: MistralClientWrapper) -> bool:

    buf1 = client.chat(
        msg.system_message_yes_no_multiple,
        msg.user_message_friend_1 + body)
    buf2 = client.chat(
        msg.system_message_yes_no_multiple,
        msg.user_message_friend_2 + body)

    return is_positive_answer(buf1) and is_positive_answer(buf2)


def screen_in_friends_and_business(
        pairs: List[object],
        client: MistralClientWrapper) -> List[object]:

    res = []
    for pair in pairs:
        for body in pair["bodies"]:
            if is_written_by_friend_and_business(body, client):
                res.append(pair)
                break
    return res


def is_sensitive_email(
        body: str,
        client: MistralClientWrapper) -> bool:

    buf = client.chat(
        msg.system_message_yes_no,
        msg.user_message_sensitive_1 + body)
    if is_positive_answer(buf):
        return True

    buf = client.chat(
        msg.system_message_yes_no,
        msg.user_message_sensitive_2 + body)
    if is_positive_answer(buf):
        return True

    return False


def screen_out_sensitive_emails(
        pairs: List[object],
        client: MistralClientWrapper) -> List[object]:

    res = []
    for pair in pairs:
        for body in pair["bodies"]:
            if is_sensitive_email(body, client):
                break
        else:
            res.append(pair)

    return res


def perform_screening(
        pairs: List[object],
        client: MistralClientWrapper) -> List[object]:

    pairs = screen_out_close_family(pairs, client)
    pairs = screen_in_friends_and_business(pairs, client)
    pairs = screen_out_sensitive_emails(pairs, client)
    return pairs


def main():
    sender_recipient_pairs = load_json()
    sender_recipient_pairs = perform_screening(
        sender_recipient_pairs, open_mistral_client())
    dump_json(sender_recipient_pairs)
    display_distinct_bodies(sender_recipient_pairs)


if __name__ == "__main__":
    main()
