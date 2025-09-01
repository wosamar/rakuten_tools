import requests
import json

from items.models import ProductData


class ProductUpdater:
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
        return resp.status_code, resp.text
