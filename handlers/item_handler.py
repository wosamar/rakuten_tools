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

    def patch_item(self, product: ProductData):
        url = self.endpoint_template.format(manageNumber=product.manage_number)
        data = product.to_patch_payload()
        resp = requests.patch(url, headers=self.headers, data=json.dumps(data))

        if resp.status_code != 204:
            raise Exception("\n".join([error.get("message") for error in resp.json().get("errors")]))

        return resp


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


if __name__ == '__main__':
    raw_dic = {k: "" for k in [5, 10, 15, 20]}
    raw_dic[20] = """
    tra-bull-01
    tra-bull-02
    tra-bull-04
    tra-bull-07
    tra-bull-06
    tra-bull-08
    tra-bull-08
    tra-bull-08
    tra-echobuckle-01
    tra-echobuckle-01
    tra-echobuckle-01
    tra-echobuckle-01
    tra-echobuckle-02
    tra-echobuckle-02
    tra-echobuckle-02
    tra-echobuckle-03
    tra-echobuckle-03
    tra-echobuckle-03
    tra-echobuckle-04
    tra-lifenergy-01
    tra-lifenergy-02
    tra-lifenergy-02
    tra-lifenergy-02
    tra-lifenergy-02
    tra-lifenergy-02
    tra-lifenergy-02
    tra-lifenergy-02
    tra-lifenergy-04
    tra-lifenergy-05
    tra-lifenergy-06
    tra-lifenergy-08
    """
    raw_dic[15] = """tra-gemcrown-01
    tra-gemcrown-02
    tra-gemcrown-03
    tra-gemcrown-04
    tra-gemcrown-05
    tra-hiq-06
    tra-bull-06
    tra-healthbody-01
    tra-healthbody-04
    tra-healthbody-05
    tra-healthbody-05
    tra-healthbody-05
    tra-healthbody-06
    tra-healthbody-07
    tra-healthbody-07
    tra-healthbody-07
    tra-healthbody-07"""
    raw_dic[10] = """
    tra-washi-04
    tra-washi-01
    tra-alody-03
    tra-tne-03
    tra-tne-04
    tra-tne-05"""
    raw_dic[5] = """
    tra-washi-02
    tra-lotboard-01
    tra-lotboard-02
    tra-lotboard-03
    tra-lotboard-04
    tra-lotboard-05
    tra-hiq-01
    tra-hiq-02
    tra-hiq-05
    tra-unemac-01
    tra-unemac-02
    tra-unemac-03
    tra-unemac-04
    tra-unemac-05
    """
    exporter = RakutenProductExporter(env_settings.auth_token)
    for p, raw in raw_dic.items():
        exporter.run(
            raw_text=raw,
            fields=["manage_number", "title", "standard_price", "reference_price"],
            csv_file=str(env_settings.output_dir / f"{p}-products.csv")
        )
        print("查詢中...")
        time.sleep(5)
