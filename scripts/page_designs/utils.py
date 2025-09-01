import json
import os
import re
import shutil
from pathlib import Path

from scripts.page_designs.models import ProductDescriptionData


def copy_html_files(folder_name, start=2, end=5):
    if not os.path.isdir(folder_name):
        print(f"{folder_name} 不存在")
        return

    html_files = [f for f in os.listdir(folder_name) if f.endswith(".html") and re.search(r"-01-", f)]
    if not html_files:
        print("找不到符合規則的 HTML 檔")
        return

    prefix_pattern = re.compile(r"^(.*?)-01-")

    for i in range(start, end + 1):
        for file_name in html_files:
            match = prefix_pattern.match(file_name)
            if not match:
                continue
            prefix = match.group(1)
            new_file_name = file_name.replace(f"{prefix}-01-", f"{prefix}-{i:02}-")
            src_path = os.path.join(folder_name, file_name)
            dst_path = os.path.join(folder_name, new_file_name)
            shutil.copy(src_path, dst_path)

            print(f"Copied {src_path} -> {dst_path}")


# TODO: euc_jp編碼
def check_eucjp(text, encoding="euc_jp"):
    result = []
    for i, char in enumerate(text):
        try:
            char.encode(encoding)
        except UnicodeEncodeError:
            result.append((i, char))
    return result


def load_product_from_json(json_path: Path) -> ProductDescriptionData:
    json_path = json_path
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    product = ProductDescriptionData(
        shop_code=data["shop_code"],
        product_id=data["product_id"],
        image_amount=data["image_amount"],
        description=data["description"],
        features=data["features"],
        highlights=data["highlights"],
        product_info=data["product_info"]
    )
    return product
