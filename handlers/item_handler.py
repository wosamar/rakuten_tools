import json
from typing import List, Dict

import requests

from env_settings import EnvSettings

env_settings = EnvSettings()


class ItemHandler:
    def __init__(self, auth_token: str):
        self.base_url = "https://api.rms.rakuten.co.jp/es/2.0/items"
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    def search_item(self, params: dict, page_size: int = 100, max_page: int = 10) -> List[Dict]:
        url = f"{self.base_url}/search"

        results = []

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

            results.extend(items)

            # 如果本頁數量小於 page_size，也代表已經抓完
            if len(items) < page_size:
                break

        return results

    def get_item(self, manage_number: str) -> dict:
        url = f"{self.base_url}/manage-numbers/{manage_number}"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()

        return resp.json()

    def patch_item(self, manage_number, payload):
        url = f"{self.base_url}/manage-numbers/{manage_number}"
        resp = requests.patch(url, headers=self.headers, data=json.dumps(payload))
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error patching item {manage_number}: {e}")
            print(f"Response content: {resp.text}")  # TODO:讓外層可以知道錯誤內容
            raise
        return resp

    def bulk_get_item(self, manage_numbers: list) -> List[Dict]:
        results = []
        url = f"{self.base_url}/bulk-get"
        chunk_size = 50

        for i in range(0, len(manage_numbers), chunk_size):
            chunk = manage_numbers[i:i + chunk_size]
            data = {"manageNumbers": chunk}
            resp = requests.post(url, headers=self.headers, data=json.dumps(data))
            resp.raise_for_status()
            results.extend(resp.json().get("results", []))

        return results

    def upsert_item(self, manage_number: str, item: Dict):
        url = f"{self.base_url}/manage-numbers/{manage_number}"
        resp = requests.put(url, headers=self.headers, data=json.dumps(item))
        resp.raise_for_status()
        return resp

    def delete_item(self, manage_number: str):
        url = f"{self.base_url}/manage-numbers/{manage_number}"
        resp = requests.delete(url, headers=self.headers)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error deleting item {manage_number}: {e}")
            print(f"Response content: {resp.text}")
            raise
        return resp
