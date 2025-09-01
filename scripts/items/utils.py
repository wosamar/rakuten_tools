import json

import requests

from env_settings import BASE_DIR

BASE_URL = "https://api.rms.rakuten.co.jp/es/2.0/items/manage-numbers"


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
    # auth = utils.get_auth_token()
    # update_variants(auth, "tra-immoto-02")

    path = BASE_DIR / "items" / "tmp" / "variants.json"
    add_default_attributes(path, BASE_DIR / "items" / "tmp" / "variants_with_attributes.json")
