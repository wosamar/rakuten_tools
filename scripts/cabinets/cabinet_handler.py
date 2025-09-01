import math
import os
import re
import time

import requests
import xml.etree.ElementTree as ET

import utils
from models import ShopInfo, FileInfo


class RakutenCabinet:
    def __init__(self, auth_token):
        self.headers = {"Authorization": f"Bearer {auth_token}"}

    def _paginate(self, url, params, count_tag, item_tag):
        params = params.copy()
        params["offset"] = 1
        resp = requests.get(url, headers=self.headers, params=params, timeout=10)
        root = ET.fromstring(resp.text)

        total = int(root.findtext(f".//{count_tag}", "0"))
        limit = int(params.get("limit", 100))
        pages = math.ceil(total / limit)

        items = root.findall(f".//{item_tag}")
        for page in range(2, pages + 1):
            params["offset"] = page
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            root = ET.fromstring(resp.text)
            items.extend(root.findall(f".//{item_tag}"))
        return items

    def extract_shops(self, sku_str):
        skus = [s.strip() for s in sku_str.strip().splitlines() if s.strip()]
        shops = {}
        for sku in skus:
            match = re.search(r"-(\w+)-\d+$", sku)
            if match:
                shop_name = match.group(1)
                if shop_name not in shops:
                    shops[shop_name] = ShopInfo(shop_name)
                shops[shop_name].add_sku(sku)
        return shops

    def get_folders(self):
        url = "https://api.rms.rakuten.co.jp/es/1.0/cabinet/folders/get"
        return self._paginate(url, {"limit": 100}, "folderAllCount", "folder")

    def match_folders(self, shops):
        folders = self.get_folders()
        for folder in folders:
            folder_name = folder.find("FolderName").text
            folder_id = folder.find("FolderId").text
            folder_path = folder.find("FolderPath").text
            for shop in shops.values():
                if shop.name in folder_name:
                    shop.folder_id = folder_id
                    shop.folder_name = folder_name
                    shop.folder_path = folder_path

    def get_files(self, shops):
        for shop in shops.values():
            if not shop.folder_id:
                continue
            url = "https://api.rms.rakuten.co.jp/es/1.0/cabinet/folder/files/get"
            items = self._paginate(url, {"folderId": shop.folder_id, "limit": 100}, "fileAllCount", "file")
            for f in items:
                file_name = f.find("FileName").text
                if any(sku in file_name for sku in shop.skus):
                    shop.files.append(FileInfo(f))

    def download_files(self, shops, save_dir="downloads"):
        os.makedirs(save_dir, exist_ok=True)
        for shop in shops.values():
            for f in shop.files:
                fname = f.file_name
                for i in range(3):
                    try:
                        resp = requests.get(f.file_url, headers=self.headers, timeout=10)
                        resp.raise_for_status()
                        path = os.path.join(save_dir, fname)
                        with open(path, "wb") as out:
                            out.write(resp.content)
                        print("✅ 下載完成:", path)
                        break
                    except requests.exceptions.RequestException as e:
                        print(f"⚠ 下載失敗 {fname}: {e}, 重試中…")
                        time.sleep(2)
                else:
                    print("❌ 多次下載失敗:", fname)

    def check_missing(self, shops):
        missing_folders = [shop.name for shop in shops.values() if not shop.folder_id]
        if missing_folders:
            print("⚠ 沒有找到資料夾的商店:", missing_folders)
        missing_files = []
        for shop in shops.values():
            missing_files.extend(shop.missing_files())
        if missing_files:
            print("⚠ 沒有找到檔案的商品:", missing_files)

    def run(self, sku_str):
        shops = self.extract_shops(sku_str)
        print("🔹 抽取商店:", list(shops.keys()))

        self.match_folders(shops)
        folder_ids = [s.folder_id for s in shops.values() if s.folder_id]
        print("🔹 找到資料夾 ID:", folder_ids)

        self.get_files(shops)
        total_files = [len(s.files) for s in shops.values()]
        print("🔹 找到檔案數量:", total_files)

        # self.download_files(shops)
        self.check_missing(shops)


if __name__ == '__main__':
    # sku_input = "twe-feca-02"
    sku_input = """
    stra-hiq-06
    tra-lifenergy-01
    tra-lifenergy-04
    tra-lifenergy-08
    twe-dc-01
    twe-feca-02
    twe-feca-04
    twe-feca-06
    twe-feca-07
    twe-feca-08
    twe-feca-09
    twe-feca-13
    twe-feca-14
    twe-feca-18
    twe-feca-19
    twe-feca-21
    twe-mosa-01
    twe-mosa-02
    twe-shinebeam-01
    """

    cabinet = RakutenCabinet(utils.get_auth_token())
    images = cabinet.run(sku_input)
