import json
from typing import List, Dict

import requests

from env_settings import EnvSettings
from models.item import ProductData

env_settings = EnvSettings()


class ItemHandler:
    def __init__(self, auth_token: str):
        self.base_url = "https://api.rms.rakuten.co.jp/es/2.0/items"
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    def search_item(self, params: dict) -> List[Dict]:
        url = f"{self.base_url}/search"

        result = []
        page_size = 100
        max_page = 10

        # 確保每頁筆數固定
        params.update({"hits": page_size})

        for page in range(max_page):
            offset = page * page_size
            params.update({"offset": offset})

            resp = requests.get(
                url,
                params=params,
                headers=self.headers
            )
            resp.raise_for_status()
            data = resp.json()

            # 拿到 results
            items = data.get("results", [])
            if not items:  # 沒有更多資料就結束
                break

            result.extend(items)

            # 如果本頁數量小於 page_size，也代表已經抓完
            if len(items) < page_size:
                break

        return result

    def get_item(self, manage_number: str) -> dict:
        url = f"{self.base_url}/manage-numbers/{manage_number}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()

        return resp.json()

    def patch_item(self, product: ProductData):
        url = f"{self.base_url}/manage-numbers/{product.manage_number}"
        data = product.to_patch_payload()
        resp = requests.patch(url, headers=self.headers, data=json.dumps(data))
        resp.raise_for_status()

        return resp

    def bulk_get_item(self, manage_numbers: list):
        url = f"{self.base_url}/bulk-get"
        data = {"manageNumbers": manage_numbers}
        resp = requests.post(url, headers=self.headers, data=json.dumps(data))

        resp.raise_for_status()

        return resp.json()


# 重置所有圖片說明
def update_alt_flow(auth_token: str, manage_number: str):
    item_handler = ItemHandler(auth_token)
    item_data = item_handler.get_item(manage_number)

    title = item_data.get("title", "")
    alt_text = title.replace(" ", "")

    images_payload = []
    shop_name = manage_number.split("-")[-2]
    for img in item_data.get("images", []):
        location = img.get("location")
        if shop_name in location:
            images_payload.append({
                "type": img.get("type"),
                "location": location,
                "alt": alt_text
            })
        else:
            images_payload.append(img)  # 避免覆蓋「海外通販」圖片

    payload = {"manage_number": manage_number, "images": images_payload}

    patch_resp = item_handler.patch_item(ProductData(**payload))

    return {"alt_text": alt_text, "resp": patch_resp}


# 更新選項
def patch_customization_option(auth_token: str, new_option: dict):
    params = {
        "isHiddenItem": "false"
    }
    item_handler = ItemHandler(auth_token)
    item_data = item_handler.search_item(params)

    manage_numbers = []

    for data in item_data:
        manage_number = data.get("item").get("manageNumber")
        options = data.get("item").get("customizationOptions", [])

        print(manage_number)

        # 檢查是否已有相同 displayName（比對前20個字）
        if any(opt.get("displayName")[:20] == new_option["displayName"][:20] for opt in options):
            print(f"跳過 {manage_number}，因為已存在相同 displayName")
            continue

        options.append(new_option)
        product = ProductData(
            manage_number=manage_number,
            customization_options=options
        )
        item_handler.patch_item(product)

        manage_numbers.append(manage_number)
        # break

    print(f"已更新{len(manage_numbers)}項商品")


if __name__ == '__main__':
    # manage_numbers = """
    # tra-gnfar-01
    # tra-gnfar-02
    # """
    # for n in manage_numbers.strip().splitlines():
    #     update_alt_flow(env_settings.auth_token, n.strip())
    #     time.sleep(2)

    new_opt = {
        'displayName': '台湾中秋節連休に伴い、9月30日（火）11時以降～10月3日（金）11時までのご注文は、10月13日（月）より順次発送いたします。10月3日（金）11時以降～2025年10月12日（日）までのご注文は、2025年10月16日（木）より順次発送いたします。詳細は店舗ページにご参照ください。',
        'inputType': 'MULTIPLE_SELECTION', 'required': True,
        'selections': [{'displayValue': '了解した。'}]
    }
    patch_customization_option(env_settings.auth_token, new_opt)
