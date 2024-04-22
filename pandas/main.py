from dotenv import load_dotenv
from icecream import ic
from jsonschema import validate
import os
import pandas as pd
from statistics import mean, median
from typing import Callable, List, Optional

import __mistral_wrapper__
from mistral_cache import MistralCache
from mistral_logger import MistralLogger
from mistral_client_wrapper import MistralClientWrapper
from mistral_client_wrapper import MistralModel

import messages as msg


input_filepath = "emails-ref.json"
output_filepath = "emails-clean.json"


json_schema = {
    "body": "string",
    "from": "string",
}


def validate_json(filepath: str):
    with open(filepath, mode="r") as fp:
        r = fp.read()
        validate(instance=r, schema=json_schema)


def open_mistral_client() -> MistralClientWrapper:
    load_dotenv()
    return MistralClientWrapper(
        os.environ["MISTRAL_API_KEY"],
        MistralModel.LARGE,
        MistralLogger(os.environ["MISTRAL_LOGGING_FILE"]),
        MistralCache(os.environ["MISTRAL_CACHE_DUMP"])
    )


def print_header(func: Callable):
    def wrapper(*args, **kwargs):
        print("=" * 80)
        print(func.__name__)
        print("=" * 80)
        res = func(*args, **kwargs)
        print()
        return res
    return wrapper


@print_header
def addresses_analysis(df: pd.DataFrame):
    dft = df.groupby("from").agg(
        nb_emails=("body", "count")).reset_index()
    ic(dft)

    dft = dft.groupby("nb_emails").agg(
        nb_senders=("from", "count")).reset_index()
    ic(dft)


@print_header
def hellos_analysis(df: pd.DataFrame):
    freqency = {}
    for body in df["body"]:
        (b0, b1) = body.split(",")[:2]

        if b0 == "Madame" and b1 == " Monsieur":
            b0 = "Madame, Monsieur"

        freqency[b0] = 1 if b0 not in freqency else freqency[b0] + 1

    total = 0
    for i, (k, v) in enumerate(sorted(freqency.items())):
        ic(i, k, v)
        total += v
    ic("Total:", total)


@print_header
def recipients_analysis(df: pd.DataFrame):
    freqency = {}
    for body in df["body"]:
        b0 = body.split(",")[0].split(" ")
        if len(b0) == 1:
            continue
        name = b0[1]

        if not name[0].isupper() or name in ["Maman", "Papa"]:
            continue

        freqency[name] = 1 if name not in freqency else freqency[name] + 1

    total = 0
    for i, (k, v) in enumerate(sorted(freqency.items())):
        ic(i, k, v)
        total += v
    ic("Total:", total)


@print_header
def bodys_analysis(df: pd.DataFrame):
    dft = df.groupby("body").agg(count=("body", "count")).reset_index()

    lines = [0] * len(dft.index)
    for i, body in enumerate(dft.loc[:, "body"]):
        lines[i] = len(body.split("\n"))

    dft["lines"] = lines
    ic(dft)
    ic([min(lines), max(lines), mean(lines), median(lines)])


def dataframe_analysis(df: pd.DataFrame):
    addresses_analysis(df)
    hellos_analysis(df)
    recipients_analysis(df)
    bodys_analysis(df)


def extract_one_recipient(
        body: str,
        client: MistralClientWrapper) -> Optional[str]:

    tmp = body[:len(body) - 32]

    system_msg = msg.system_message_recipient
    user_msg = msg.user_message_recipient + tmp
    res = client.chat(system_msg, user_msg)

    if "NON" in res:
        return None
    if len(res.split(" ")) > 1:
        # Here we should log oddities
        return None

    return res


def extract_recipients(
        df: pd.DataFrame,
        client: MistralClientWrapper) -> List[Optional[str]]:

    res = [0] * len(df.index)
    for i, body in enumerate(df.loc[:, "body"]):
        res[i] = extract_one_recipient(body, client)
    return res


def insert_recipients(df: pd.DataFrame, recipients: List[Optional[str]]):
    df["recipient"] = recipients


def select_not_null_recipients(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["recipient"].notnull()].reset_index()


def group_by_hash_from_and_recipient(df: pd.DataFrame) -> pd.DataFrame:
    gb = df.groupby(["from", "recipient"])["body"]
    return gb.apply(list).reset_index(name="bodies")


def extract_one_sender(
        body: str,
        client: MistralClientWrapper) -> Optional[str]:

    tmp = body[min(body.find(","), 32):]

    system_msg = msg.system_message_sender
    user_msg = msg.user_message_sender + tmp
    res = client.chat(system_msg, user_msg)

    if "NON" in res:
        return None
    if len(res.split(" ")) > 1:
        # Here we should log oddities
        return None

    return res.replace(".", "")


def extract_senders(
        df: pd.DataFrame,
        client: MistralClientWrapper) -> List[Optional[str]]:

    res = [0] * len(df.index)
    for i, bodies in enumerate(df.loc[:, "bodies"]):
        for body in bodies:
            res[i] = extract_one_sender(body, client)
            if res[i] is not None:
                break
    return res


def insert_senders(df: pd.DataFrame, senders: List[Optional[str]]):
    df["sender"] = senders


def select_not_null_senders(df: pd.DataFrame):
    return df[df["sender"].notnull()].reset_index()


def rearrange_dataframe(
        df: pd.DataFrame,
        client: MistralClientWrapper) -> pd.DataFrame:

    recipients = extract_recipients(df, client)
    insert_recipients(df, recipients)
    df = select_not_null_recipients(df)

    df = group_by_hash_from_and_recipient(df)

    senders = extract_senders(df, client)
    insert_senders(df, senders)
    df = select_not_null_senders(df)

    return df


def main():
    validate_json(input_filepath)
    df = pd.read_json(input_filepath)
    dataframe_analysis(df)
    df = rearrange_dataframe(df, open_mistral_client())
    df.to_json(output_filepath, orient="records")


if __name__ == "__main__":
    main()
