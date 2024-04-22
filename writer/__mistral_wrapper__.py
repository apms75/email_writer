from pathlib import Path as __loader_path
from sys import path as __loader_syspath

__loader_syspath.append(str(__loader_path(__file__).parent.resolve().parent / "mistral" / "modules"))
