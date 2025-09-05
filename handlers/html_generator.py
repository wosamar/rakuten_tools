from database import Product


class HTMLGenerator:
    base_cabinet_url: str = "https://image.rakuten.co.jp/giftoftw/cabinet/"

    def __init__(self, template_path: str):
        self.template_path = template_path
        self.template = self._load_template()

    def _load_template(self) -> str:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_html(self, product: Product) -> str:
        """
        接收 Product ORM 物件，回傳 HTML 字串
        """
        # ======= 轉換圖片 =======
        images_html = "\n".join([
            f'<img src="https://image.rakuten.co.jp/giftoftw/cabinet/{product.shop.name}/{img.file_name}" width="100%">'
            for img in product.images
        ])

        # ======= 轉換描述 =======
        # description 與 feature 假設存成 list 或以換行拆成多段
        desc_html = "\n".join([f"<p>{p}</p>" for p in product.description.split("\n")])
        features_html = "\n".join([f"<p><b>{k}</b><br>{v}</p>" for k, v in product.feature_dict.items()]) if hasattr(
            product, "feature_dict") else f"<p>{product.feature}</p>"

        # ======= 轉換 highlight =======
        highlights_html = "<br><br>\n".join(
            [f"{i + 1}. {h}" for i, h in enumerate(product.highlight.strip().split("\n"))]) + "<br><br>"

        # ======= 轉換 info =======
        info_html = "\n".join([
            f'<tr><th width="30%" bgcolor="#EEE">{k}</th><td bgcolor="#fff">{v.replace("\n", "<br>")}</td></tr>'
            for k, v in product.info_dict.items()
        ])

        # ======= 替換模板 =======
        html_final = self.template
        html_final = html_final.replace("{{IMAGES}}", images_html)
        html_final = html_final.replace("{{DESCRIPTION}}", desc_html)
        html_final = html_final.replace("{{FEATURES}}", features_html)
        html_final = html_final.replace("{{HIGHLIGHTS}}", highlights_html)
        html_final = html_final.replace("{{PRODUCT_INFO}}", info_html)

        return html_final
