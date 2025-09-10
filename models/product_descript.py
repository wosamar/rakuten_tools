from pathlib import Path

from env_settings import EnvSettings

env_settings = EnvSettings()
cabinet_prefix = f"https://image.rakuten.co.jp/{env_settings.TENPO_NAME}/cabinet"


class ProductDescriptionData:
    def __init__(self, shop_code: str, image_infos: list,
                 description: str, feature: str, highlight: str, product_info: dict):
        self.shop_code = shop_code
        self.image_infos = self._build_image_infos(shop_code, image_infos)
        self.description = [p.strip() for p in description.splitlines() if p.strip()]
        self.feature = [f.strip() for f in feature.splitlines() if f.strip()]
        self.highlight = [h.strip() for h in highlight.splitlines() if h.strip()]
        self.product_info = product_info

    @staticmethod
    def _build_image_infos(shop_code: str, image_infos: list):
        result = []
        shop_name = shop_code.split("-")[-1]
        for image_info in image_infos:
            full_url = f"{cabinet_prefix}/{shop_name}/{image_info.get('url')}"
            result.append({"url": full_url, "description": image_info.get("description")})
        return result

    @classmethod
    def from_json(cls, json_path: Path):
        import json
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            shop_code=data["shop_code"],
            image_infos=data["images"],
            image_descriptions=data["image_descriptions"],
            description=data.get("description"),
            feature=data.get("features"),
            highlight=data.get("highlights"),
            product_info=data.get("product_info")
        )

    def to_dict(self):
        return {
            "shop_code": self.shop_code,
            "image_infos": self.image_infos,
            "description": self.description,
            "features": self.feature,
            "highlights": self.highlight,
            "product_info": self.product_info
        }
