import requests

from env_settings import EnvSettings

env_settings = EnvSettings()


def update_category_layout():
    headers = {
        "Authorization": f"Bearer {env_settings.auth_token}",
        "Content-Type": "application/json"
    }
    tree_url = "https://api.rms.rakuten.co.jp/es/2.0/categories/shop-category-trees/category-set-ids/0"
    resp = requests.get(tree_url, headers=headers)

    categories = resp.json().get("rootNode").get("children")
    root_category_ids = [category.get("categoryId") for category in categories]
    print(root_category_ids)

    detail_url = "https://api.rms.rakuten.co.jp/es/2.0/categories/shop-categories/category-ids/{uuid}"
    for i in root_category_ids:
        resp = requests.get(detail_url.format(uuid=i), headers=headers)
        resp.raise_for_status()

        if "◆" in resp.json().get("title"):
            print(resp.json())



if __name__ == '__main__':
    update_category_layout()
