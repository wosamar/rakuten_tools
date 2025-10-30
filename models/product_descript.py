from env_settings import EnvSettings

env_settings = EnvSettings()


class ImageInfo:
    def __init__(self, image_url: str, description: str, link: str):
        self.image_url = image_url
        self.description = description
        self.link = link


class ProductDescriptionData:
    def __init__(self, shop_code: str, image_infos: list,
                 description: str, feature: str, highlight: str, product_info: dict):
        self.shop_code = shop_code
        self.image_infos = [ImageInfo(**info) for info in image_infos]
        self.description = [p.strip() for p in description.splitlines() if p.strip()]
        self.feature = [f.strip() for f in feature.splitlines() if f.strip()]
        self.highlight = [h.strip() for h in highlight.splitlines() if h.strip()]
        self.product_info = product_info

    def to_dict(self):
        return {
            "shop_code": self.shop_code,
            "image_infos": self.image_infos,
            "description": self.description,
            "features": self.feature,
            "highlights": self.highlight,
            "product_info": self.product_info
        }
