import json
from pathlib import Path

from scripts.page_designs.models import ProductDescriptionData


# TODO: euc_jp編碼
def check_eucjp(text, encoding="euc_jp"):
    result = []
    for i, char in enumerate(text):
        try:
            char.encode(encoding)
        except UnicodeEncodeError:
            result.append((i, char))
    return result
