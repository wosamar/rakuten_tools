import json
from typing import List, Dict, Tuple

import requests
from requests.packages import target

from env_settings import EnvSettings
from handlers.item_handler import ItemHandler
from models.item import ProductData

BASE_URL = "https://api.rms.rakuten.co.jp/es/2.0/items/manage-numbers"
env_settings = EnvSettings()


# 檢查　指定欄位　是否包含　指定字串（如1024mr)
def check_event_info_updated(items, target_text: str, column_name: str) -> Tuple[
    List[Dict], List[Dict]]:
    updated_items = []
    not_updated_items = []
    for item in items:
        item = item.get("item") or item
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
    # ids = ["tra-gemcrown-04", "tra-gemcrown-05", "tra-chauwan-01", "tra-chauwan-02", "tra-chauwan-07", "tra-chauwan-08",
    #        "tra-wanwen-01", "tra-wanwen-02", "tra-wanwen-03", "tra-wanwen-04", "tra-wanwen-05", "tra-ambassador-02",
    #        "tra-yzuyanghsuan-01", "tra-yzuyanghsuan-02", "tra-yzuyanghsuan-03", "tra-yzuyanghsuan-04",
    #        "tra-yzuyanghsuan-05", "tra-tongwang-01", "tra-tongwang-02", "tra-tongwang-06", "tra-encens-set01",
    #        "tra-encens-snake01", "tra-encens-snake02", "tra-encens-snake04", "tra-encens-snake05", "cheerful-candy_01",
    #        "cheerful-candy_02", "cheerful-candy_03", "cheerful-candy_04", "cheerful-candy_2set", "cheerful-candy_3set",
    #        "cheerful-candy_4set", "10dksfood 32"]
    # items = item_handler.bulk_get_item(ids)

    # upt_items, not_upt_items = check_event_info_updated(items, "1024mr", "salesDescription")
    targets = ["10dksdriink", "10dksfood", "10dksbook"]
    for target in targets:
        upt_items, not_upt_items = check_event_info_updated(items, target, "title")

        print(target)
        print(f"含指定文字：{len(upt_items)},不含指定文字：{len(not_upt_items)}")
        print(f"不含指定文字的商品：{[list(i.keys())[0] for i in not_upt_items]}")
        print("========")
        # for not_upt_item in not_upt_items:
        #     manage_number = list(not_upt_item.keys())[0]
        #     original_title = not_upt_item[manage_number]["title"]
        #     payload = {
        #         "title": original_title.replace("10dksdriink", "10dksfood")
        #     }
        #     # item_handler.patch_item(manage_number, payload)
        #
        #     print(manage_number, payload)

    # o_text = "<a href=\"https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/\"><img src=\"1024mr_kv_1280.jpg\"width=\"100%\"/a>"
    # n_text = "<a href=\"https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/\"><img src=\"https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_kv_1280.jpg\"width=\"100%\"/></a>"
    # replace_text(items, o_text, n_text)

    # path = BASE_DIR / "items" / "tmp" / "variants.json"
    # add_default_attributes(path, BASE_DIR / "items" / "tmp" / "variants_with_attributes.json")
