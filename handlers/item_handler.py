import csv
import json
import time
from pathlib import Path
from typing import List, Dict

import requests

from env_settings import EnvSettings
from models.item import ProductData

env_settings = EnvSettings()


class ItemHandler:
    def __init__(self, auth_token: str):
        self.endpoint_template = "https://api.rms.rakuten.co.jp/es/2.0/items/manage-numbers/{manageNumber}"
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    def get_item(self, manage_number: str) -> dict:
        url = self.endpoint_template.format(manageNumber=manage_number)
        resp = requests.get(url, headers=self.headers)
        if resp.status_code != 200:
            raise Exception(f"GET failed: {resp.status_code}, {resp.text}")
        return resp.json()

    def patch_item(self, product: ProductData):
        url = self.endpoint_template.format(manageNumber=product.manage_number)
        data = product.to_patch_payload()
        resp = requests.patch(url, headers=self.headers, data=json.dumps(data))

        if resp.status_code != 204:
            raise Exception("\n".join([error.get("message") for error in resp.json().get("errors")]))

        return resp


# TODO:重構ItemHandler
class RakutenProductExporter:
    def __init__(self, auth_token: str):
        self.url = "https://api.rms.rakuten.co.jp/es/2.0/items/bulk-get"
        self.headers = {"Authorization": f"Bearer {auth_token}"}

    def _parse_input(self, raw_text: str) -> List[str]:
        lines = list(set(raw_text.splitlines()))
        return [s.strip() for s in lines if s.strip()]

    def fetch_products(self, manage_numbers: List[str]) -> Dict[str, "ProductData"]:
        res = requests.post(self.url, json={"manageNumbers": manage_numbers}, headers=self.headers)
        data = res.json()

        if res.status_code != 200:
            print(f"Status code: {res.status_code}")  # 印出回傳狀態碼
            print(data)

        result = {}
        for item in data.get("results", []):
            product = ProductData.from_api(item)
            result[item.get("manageNumber")] = product
        return result

    def download_images(self, products: Dict[str, "ProductData"], save_dir="images"):
        Path(save_dir).mkdir(exist_ok=True)
        for manage_no, product in products.items():
            for idx, img in enumerate(product.images, start=1):
                url = img.location
                ext = url.split(".")[-1]
                img_path = Path(save_dir) / f"{manage_no}_{idx}.{ext}"
                try:
                    r = requests.get(url)
                    r.raise_for_status()
                    img_path.write_bytes(r.content)
                except Exception:
                    continue

    def export_csv(self, products: Dict[str, "ProductData"], fields: List[str], csv_file="products.csv"):
        results = [{f: getattr(p, f, None) for f in fields} for p in products.values()]
        csv_path = Path(csv_file)
        csv_path.parent.mkdir(parents=True, exist_ok=True)  # 確保資料夾存在
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(results)
        print(f"完成！資料存於 {csv_path}")

    def run(self, raw_text: str, fields: List[str],
            save_dir="images", download_images=False,
            csv_file="products.csv"):
        manage_numbers = self._parse_input(raw_text)
        products = self.fetch_products(manage_numbers)
        if download_images:
            self.download_images(products, save_dir)
        self.export_csv(products, fields, csv_file)

        found = list(products.keys())
        not_found = [m for m in manage_numbers if m not in found]
        total_images = sum(len(p.images) for p in products.values())

        return {
            "total_images": total_images,
            "found": found,
            "not_found": not_found,
            "save_dir": save_dir,
            "products": products.values()
        }


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


if __name__ == '__main__':
    manage_numbers = """
    tra-gnfar-01
    tra-gnfar-02
    """
    for n in manage_numbers.strip().splitlines():
        update_alt_flow(env_settings.auth_token, n.strip())
        time.sleep(2)
