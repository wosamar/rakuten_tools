from models.product_descript import ProductDescriptionData


class HTMLGenerator:
    base_cabinet_url: str = "https://image.rakuten.co.jp/giftoftw/cabinet/"

    def __init__(self, template_path: str):
        self.template_path = template_path
        self.template = self._load_template()

    def _load_template(self) -> str:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_html(self, product: ProductDescriptionData, is_mobile: bool = False) -> str:
        """
        接收 Product ORM 物件，回傳 HTML 字串
        手機板有可使用之元素限制
        """
        # ======= 轉換圖片 =======
        htmls = []
        for image_info in product.image_infos:
            if img_desc := image_info.get("description"):
                for desc in img_desc.splitlines():
                    if is_mobile:
                        htmls.append(f'<p>{desc}</p>')
                    else:
                        htmls.append(f'<p style="font-size:24px">{desc}</p>')
            htmls.append(f'<img src="{image_info["url"]}" width="100%">')

        images_html = "\n".join(htmls)

        # ======= 轉換描述 =======
        # description 與 feature 假設存成 list 或以換行拆成多段
        desc_html = "\n".join([f"<p>{p}</p>" for p in product.description])
        features_html = "\n".join([f"<p>{p}</p>" for p in product.feature])

        # ======= 轉換 highlight =======
        highlights_html = "<br><br>\n".join(
            [f"{i + 1}. {h}" for i, h in enumerate(product.highlight)]) + "<br><br>"

        # ======= 轉換 info =======
        info_html = "\n".join([
            f'<tr><th width="30%" bgcolor="#EEE">{k}</th><td bgcolor="#fff">{v.replace("\n", "<br>")}</td></tr>'
            for k, v in product.product_info.items()
        ])

        # ======= 替換模板 =======
        html_final = self.template
        html_final = html_final.replace("{{IMAGES}}", images_html)
        html_final = html_final.replace("{{DESCRIPTION}}", desc_html)
        html_final = html_final.replace("{{FEATURES}}", features_html)
        html_final = html_final.replace("{{HIGHLIGHTS}}", highlights_html)
        html_final = html_final.replace("{{PRODUCT_INFO}}", info_html)

        return html_final
