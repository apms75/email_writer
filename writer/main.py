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


input_filepath = "emails-screening.json"
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


def display_distinct_attributes(pairs: List[object], keyword: str):
    emails = set()
    for pair in pairs:
        emails.add(pair[keyword])

    for i, email in enumerate(emails):
        print("=" * 80)
        print(f"{i + 1}. {email}")


def extract_k_first_results(k: int, s: str) -> Optional[List[str]]:
    res = []
    for line in s.split("\n"):
        for word in line.split():
            if not word[0].isalpha():
                continue
            res.append(word)
            k -= 1
            if k == 0:
                return res
    return None


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


def extract_one_pair_styles(
        pair: object,
        client: MistralClientWrapper) -> Optional[List[str]]:

    tmp = []
    for body in pair["bodies"]:
        ans = client.chat(
            msg.system_message_style,
            msg.user_message_style_1 + body)
        tmp.extend(extract_k_first_results(3, ans) or [])
        ans = client.chat(
            msg.system_message_style,
            msg.user_message_style_2 + body)
        tmp.extend(extract_k_first_results(3, ans) or [])

    return [x[0] for x in Counter(tmp).most_common(3)]


def extract_emails_styles(
        pairs: List[object],
        client: MistralClientWrapper) -> List[str]:

    return generate_list(pairs, client, extract_one_pair_styles)


def extract_one_pair_register(
        pair: object,
        client: MistralClientWrapper) -> Optional[List[str]]:

    tmp = []
    for body in pair["bodies"]:
        ans = client.chat(
            msg.system_message_register,
            msg.user_message_register + body)
        tmp.extend(extract_k_first_results(1, ans) or [])

    return Counter(tmp).most_common(1)[0][0]


def extract_emails_registers(
        pairs: List[object],
        client: MistralClientWrapper) -> List[str]:

    return generate_list(pairs, client, extract_one_pair_register)


def generate_one_email(pair: object, client: MistralClientWrapper) -> str:
    system_msg = message_printf(msg.system_message_email, [
        ("[sender]", pair["recipient"]),
        ("[recipient]", pair["sender"]),
        ("[register]", pair["register"])])

    user_msg = message_printf(msg.user_message_email, [
        ("[style1]", pair["styles"][0]),
        ("[style2]", pair["styles"][1]),
        ("[style3]", pair["styles"][2]),
        ("[email_template]", msg.email_template),
        ("[sender]", pair["recipient"])])

    return client.chat(system_msg, user_msg)


def generate_emails(pairs: List[object],
                    client: MistralClientWrapper) -> List[str]:

    return generate_list(pairs, client, generate_one_email)


def build_example(pair: object) -> str:
    res = ""
    for body in pair["bodies"]:
        res += body + "\n"
    return res


def generate_one_email_alt(pair: object, client: MistralClientWrapper) -> str:
    system_msg = message_printf(msg.system_message_email_alt, [
        ("[example]", build_example(pair)),
        ("[sender]", pair["recipient"]),
        ("[recipient]", pair["sender"])])

    user_msg = message_printf(msg.user_message_email_alt, [
        ("[email_template]", msg.email_template),
        ("[sender]", pair["recipient"])])

    print(system_msg)

    print(user_msg)
    return client.chat(system_msg, user_msg)


def generate_emails_alt(
        pairs: List[object],
        client: MistralClientWrapper) -> List[str]:

    return generate_list(pairs, client, generate_one_email_alt)


def main():
    sender_recipient_pairs = load_json()

    styles = extract_emails_styles(
        sender_recipient_pairs,
        open_mistral_client())
    insert_attribute(sender_recipient_pairs, "styles", styles)
    registers = extract_emails_registers(
        sender_recipient_pairs,
        open_mistral_client())
    insert_attribute(sender_recipient_pairs, "register", registers)

    emails = generate_emails(
        sender_recipient_pairs,
        open_mistral_client())
    insert_attribute(sender_recipient_pairs, "email", emails)

    emails_alt = generate_emails_alt(
        sender_recipient_pairs,
        open_mistral_client())
    insert_attribute(sender_recipient_pairs, "email_alt", emails_alt)

    dump_json(sender_recipient_pairs)

    display_distinct_attributes(sender_recipient_pairs, "email")
    display_distinct_attributes(sender_recipient_pairs, "email_alt")


if __name__ == "__main__":
    main()
