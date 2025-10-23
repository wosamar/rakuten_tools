import json
from typing import List, Dict

import requests

from env_settings import BASE_DIR, EnvSettings
from handlers.item_handler import ItemHandler
from models.item import ProductData

BASE_URL = "https://api.rms.rakuten.co.jp/es/2.0/items/manage-numbers"
env_settings = EnvSettings()


# 檢查　指定欄位　是否包含　指定字串（如1024mr)
def check_event_info_updated(items, target_text: str, column_name: str = "salesDescription") -> List[Dict]:
    updated_items = []
    not_updated_items = []
    for item in items:
        item = item.get("item")
        if target_text in item.get(column_name, ""):
            updated_items.append({
                item.get("manageNumber"): {column_name: item.get(column_name)},
            })
        else:
            not_updated_items.append({
                item.get("manageNumber"): {column_name: item.get(column_name)},
            })

    return updated_items, not_updated_items


def replace_text(items, old_text, new_text):
    for item in items[:10]:
        item_data = ProductData.from_api(item.get("item"))

        sd = item_data.sales_description
        sp = item_data.product_description.sp

        payload = {
            "productDescription": {
                "sp": sp.replace(old_text, new_text),
            },
            "salesDescription": sd.replace(old_text, new_text)
        }

        print(payload)


def update_variants(auth_token: str, manage_number: str, variants: dict = None):
    """
    更新指定商品的 variants
    """
    url = f"{BASE_URL}/{manage_number}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {"variants": variants or {}}

    resp = requests.patch(url, headers=headers, json=payload)

    if resp.ok:
        return resp.json()
    else:
        raise Exception(f"API error {resp.status_code}: {resp.text}")


def add_default_attributes(input_file: str, output_file: str = None):
    """
    讀取 JSON 檔，給每個 variant 加上固定 attributes，並寫回檔案。
    若 output_file 為 None，則覆蓋原檔。
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    default_attributes = [
        {"name": "ブランド名", "values": ["immoto"]},
        {"name": "メーカー型番", "values": ["-"]},
        {"name": "代表カラー", "values": ["ブラック"]}
    ]

    for variant in data.get("variants", {}).values():
        variant["attributes"] = default_attributes

    out_file = output_file or input_file
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    item_handler = ItemHandler(env_settings.auth_token)
    items = item_handler.search_item({"isHiddenItem": "false"}, 100, 10)

    upt_items, not_upt_items = check_event_info_updated(items, "1024mr")
    # upt_items, not_upt_items = check_event_info_updated(items, "】", "title")

    print(f"含指定文字：{len(upt_items)},不含指定文字：{len(not_upt_items)}")
    print(f"不含指定文字的商品：{not_upt_items}")
    # for not_upt_item in not_upt_items:
    #     manage_number = list(not_upt_item.keys())[0]
    #     original_title = not_upt_item[manage_number]["title"]
    #     payload = {
    #         "title": original_title + "【台湾直送】【送料無料】10dksdriink"
    #     }
    #     item_handler.patch_item(manage_number, payload)
    #
    #     print(manage_number, payload)

    # o_text = "<a href=\"https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/\"><img src=\"1024mr_kv_1280.jpg\"width=\"100%\"/a>"
    # n_text = "<a href=\"https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/\"><img src=\"https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_kv_1280.jpg\"width=\"100%\"/></a>"
    # replace_text(items, o_text, n_text)

    # update_variants(env_settings.auth_token, "tra-immoto-02")

    # path = BASE_DIR / "items" / "tmp" / "variants.json"
    # add_default_attributes(path, BASE_DIR / "items" / "tmp" / "variants_with_attributes.json")
