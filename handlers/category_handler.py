import json

import requests


class CategoryHandler:
    def __init__(self, auth_token):
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.rms.rakuten.co.jp/es/2.0/categories/item-mappings/manage-numbers/"

    def get_category_mapping(self, manage_number, include_breadcrumb=False):
        """
        商品管理番号を指定し、カテゴリとの紐付き情報を取得します。
        """
        params = {
            "breadcrumb": include_breadcrumb
        }

        url = f"{self.base_url}{manage_number}"

        response = requests.get(url, headers=self.headers, params=json.dumps(params))
        response.raise_for_status()
        return response.json()

    def update_category_mapping(self, manage_number, category_ids, main_plural_category_id=None):
        """
        指定した商品管理番号の表示先カテゴリの登録や変更をすることができます。
        """
        payload = {
            "categoryIds": category_ids
        }
        if main_plural_category_id:
            payload["mainPluralCategoryId"] = main_plural_category_id

        url = f"{self.base_url}{manage_number}"
        response = requests.put(url, headers=self.headers, json=payload)
        response.raise_for_status()
