import json
import requests
from typing import List, Dict


class InventoryHandler:
    def __init__(self, auth_token: str):
        self.base_url = "https://api.rms.rakuten.co.jp/es/2.1/inventories"
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    def get_variant_list(self, manage_number: str) -> dict:
        """
        商品管理番号を指定し、在庫情報として保持している全てのSKU管理番号を取得します。

        Args:
            manage_number (str): 商品管理番号。

        Returns:
            dict: 包含 SKU 管理編號的庫存資訊。
        """
        url = f"{self.base_url}/variant-lists/manage-numbers/{manage_number}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def bulk_get_inventory(self, inventories: List[Dict]) -> dict:
        """
        商品管理番号とSKU管理番号を指定し、最大で1000件の在庫数、出荷リードタイム、配送リードタイム関連の情報を一括で取得します。

        Args:
            inventories (List[Dict]): 包含 manageNumber 和 variantId 的字典列表。
                                     例如：[{"manageNumber": "item1", "variantId": "sku1"}, ...]

        Returns:
            dict: 包含庫存資訊的字典。
        """
        url = f"{self.base_url}/bulk-get"
        payload = {
            "inventories": inventories
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()

    def bulk_upsert(self, inventories: List[Dict]):
        """
        商品管理番号とSKU管理番号を指定し、最大で400件の在庫数、出荷リードタイム、配送リードタイム関連の情報を一括で登録・更新することができます。
        部分更新の機能ではないため、リクエストに含まれない項目は値が削除されます。

        Args:
            inventories (List[Dict]): 在庫情報リスト.
                                     e.g. [
                                        {
                                            "manageNumber": "item1",
                                            "variantId": "sku1",
                                            "mode": "ABSOLUTE",
                                            "quantity": 100
                                        }, ...
                                     ]

        Returns:
            dict: APIからの応答。
        """
        url = f"{self.base_url}/bulk-upsert"
        payload = {
            "inventories": inventories
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(payload))

        response.raise_for_status()
