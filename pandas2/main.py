from dotenv import load_dotenv
import os
import pandas as pd
from typing import Tuple, List, Optional

import __mistral_wrapper__
from mistral_cache import MistralCache
from mistral_logger import MistralLogger
from mistral_client_wrapper import MistralClientWrapper
from mistral_client_wrapper import MistralModel

import messages as msg


input_filepath = "emails-ref.json"
output_filepath = "emails-clean.json"


new_columns = {
    0: "sender",
    1: "sender_name",
    2: "recipient",
    3: "recipient_name",
    4: "relationship",
}


def open_mistral_client() -> MistralClientWrapper:
    load_dotenv()
    return MistralClientWrapper(
        os.environ["MISTRAL_API_KEY"],
        MistralModel.LARGE,
        MistralLogger(os.environ["MISTRAL_LOGGING_FILE"]),
        MistralCache(os.environ["MISTRAL_CACHE_DUMP"])
    )


def display_distinct_attributes(pairs: List[object], keyword: str):
    emails = set()
    for pair in pairs:
        emails.add(pair[keyword])

    for i, email in enumerate(emails):
        print("=" * 80)
        print(f"{i + 1}. {email}")


def message_printf(msg: str, values: List[object]) -> str:
    for v in values:
        msg = msg.replace(v[0], v[1])
    return msg


def extract_k_first_results(k: int, separator: str, s: str) -> List[str]:
    res = [""] * k
    for i in range(0, k):
        x = s.find(separator)
        if x < 0:
            break
        s = s[x + len(separator):]
        x = s.find("\n")
        if x < 0:
            res[i] = s.strip()
            break
        res[i] = s[:x].strip()
    return res


def format_result(s: str) -> Optional[str]:
    if s.find("Inconnu") >= 0:
        return None
    if s.find("Vous") >= 0:
        return None
    return s


def extract_one_email_infos(
        body: str,
        client: MistralClientWrapper) -> List[Optional[str]]:

    user_msg = message_printf(msg.user_message_extract_infos_1, [
        ("[message]", body)])

    infos = extract_k_first_results(7, "Réponse:", client.chat(user_msg))

    user_msg = message_printf(msg.user_message_extract_infos_2, [
        ("[message]", body),
        ("[info1]", infos[0]),
        ("[info2]", infos[1]),
        ("[info3]", infos[2]),
        ("[info4]", infos[3]),
        ("[info5]", infos[4]),
        ("[info6]", infos[5]),
        ("[info7]", infos[6])])

    res = extract_k_first_results(5, "Réponse:", client.chat(user_msg))

    return [format_result(r) for r in res]


def extract_emails_infos(
        df: pd.DataFrame,
        client: MistralClientWrapper) -> Tuple[List[str]]:

    res = [[]] * len(df)
    for i, body in enumerate(df.loc[:, "body"]):
        res[i] = extract_one_email_infos(body, client)

    return res


def rearrange_dataframe(
        df: pd.DataFrame,
        client: MistralClientWrapper) -> pd.DataFrame:

    df = df.drop(columns=["from"])
    df = df.drop_duplicates().reset_index()

    infos = extract_emails_infos(df, client)
    for k, v in new_columns.items():
        df[v] = [i[k] for i in infos]

    return df


def main():
    df = pd.read_json(input_filepath)
    df = rearrange_dataframe(df, open_mistral_client())
    df.to_json(output_filepath, orient="records")
    print(df)


if __name__ == "__main__":
    main()
