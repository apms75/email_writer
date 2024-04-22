from dotenv import load_dotenv
import os

import __mistral_wrapper__
from mistral_cache import MistralCache
from mistral_logger import MistralLogger
from mistral_client_wrapper import MistralClientWrapper
from mistral_client_wrapper import MistralModel


def open_mistral_client() -> MistralClientWrapper:
    load_dotenv()
    return MistralClientWrapper(
        os.environ["MISTRAL_API_KEY"],
        MistralModel.LARGE,
        MistralLogger(os.environ["MISTRAL_LOGGING_FILE"]),
        MistralCache(os.environ["MISTRAL_CACHE_DUMP"])
    )


def test01(client: MistralClientWrapper):
    res = client.chat("Quels sont les 4 points cardinaux ?")
    print("=" * 80)
    print(res)


def test02(client: MistralClientWrapper):
    res = client.chat("Quels sont les 4 couleurs de cartes ?")
    print("=" * 80)
    print(res)


def test03(client: MistralClientWrapper):
    system = """Tu écris comme Jacques Prévert.
        Indiquer le nombre de pieds à la fin du poême."""
    user = "Ecris un poême de 4 vers sur le printemps."
    res = client.chat(system, user)
    print("=" * 80)
    print(res)


def test04(client: MistralClientWrapper):
    system = """Tu écris comme François Villon.
        Ecrire seulement le poême et ne rien ajouter après."""
    user = "Ecris un poême de 4 vers sur le printemps."
    res = client.chat(system, user)
    print("=" * 80)
    print(res)


def main():
    client = open_mistral_client()
    test01(client)
    test02(client)
    test03(client)
    test04(client)


if __name__ == "__main__":
    main()
