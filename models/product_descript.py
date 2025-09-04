from pathlib import Path

cabinet_prefix = "https://image.rakuten.co.jp/giftoftw/cabinet"


class ProductDescriptionData:
    def __init__(self, shop_code, product_id, image_amount,
                 description, features, highlights, product_info):
        self.shop_code = shop_code
        self.product_id = product_id

        self.images = self._build_image_urls(shop_code, product_id, image_amount)
        self.description = [p.strip() for p in description if p.strip()]
        self.features = [{"title": "", "content": f.strip()} for f in features if f.strip()]
        self.highlights = [h.strip() for h in highlights if h.strip()]
        self.product_info = [{"name": k, "value": v} for k, v in product_info.items()]

    @staticmethod
    def _build_image_urls(shop_code: str, product_id: str, image_amount):
        urls = []
        shop_en = shop_code.split("-")[-1]
        for i in range(image_amount):
            img_path = f"{shop_code}-{product_id}_{i + 1:02}.jpg"
            full_url = f"{cabinet_prefix}/{shop_en}/{img_path}"
            urls.append(full_url)
        return urls

    @classmethod
    def from_json(cls, json_path: Path):
        import json
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            shop_code=data["shop_code"],
            product_id=data["product_id"],
            image_amount=data.get("image_amount"),
            description=data.get("description"),
            features=data.get("features"),
            highlights=data.get("highlights"),
            product_info=data.get("product_info")
        )

    def to_dict(self):
        return {
            "images": self.images,
            "description": self.description,
            "features": self.features,
            "highlights": self.highlights,
            "product_info": self.product_info
        }
