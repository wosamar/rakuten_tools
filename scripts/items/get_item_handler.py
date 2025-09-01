import os
import requests
import utils
from scripts.items.models import ProductImage, ProductData


class RakutenImageFetcher:
    def __init__(self, auth_token:str):
        self.url = "https://api.rms.rakuten.co.jp/es/2.0/items/bulk-get"
        self.headers = {"Authorization": f"Bearer {auth_token}"}

    def _parse_input(self, raw_text):
        return [s.strip() for s in raw_text.splitlines() if s.strip()]

    def fetch_products(self, manage_numbers):
        res = requests.post(self.url, json={"manageNumbers": manage_numbers}, headers=self.headers)
        data = res.json()
        result = {}
        for item in data.get("results", []):
            manage_no = item.get("manageNumber")
            images = [
                ProductImage(type=img["type"], location=img["location"], alt=img.get("alt", ""))
                for img in item.get("images", [])
            ]
            tags = [str(tag) for tag in item.get("tags", [])]
            product = ProductData(
                manage_number=manage_no,
                item_number=item.get("itemNumber"),
                title=item.get("title"),
                tagline=item.get("tagline", ""),
                product_description=item.get("productDescription", {}),
                sales_description=item.get("salesDescription", ""),
                images=images,
                genre_id=item.get("genreId", ""),
                tags=tags
            )
            result[manage_no] = product
        return result

    def download_images(self, products: dict, save_dir="images"):
        os.makedirs(save_dir, exist_ok=True)
        for manage_no, product in products.items():
            for idx, img in enumerate(product.images, start=1):
                filename = os.path.join(save_dir, f"{manage_no}_{idx}.jpg")
                url = "https://image.rakuten.co.jp/giftoftw/cabinet" + img.location
                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    with open(filename, "wb") as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)

    def run(self, raw_text, save_dir="images", download=True):
        manage_numbers = self._parse_input(raw_text)
        products = self.fetch_products(manage_numbers)

        if download:
            self.download_images(products, save_dir)

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
    raw = """
    tra-hiq-06
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

    token = utils.get_auth_token()
    fetcher = RakutenImageFetcher(token)
    res = fetcher.run(raw, download=False)
    print(
        res["total_images"],
        res["found"],
        res["not_found"],
        res["save_dir"],
        # result["products"]
    )
    for p in res["products"]:
        print(p.title)