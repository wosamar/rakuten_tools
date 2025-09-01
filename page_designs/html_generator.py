class HTMLGenerator:
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.template = self._load_template()

    def _load_template(self) -> str:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_html(self, product: dict, output_path: str):
        # ======= 將物件內容轉成 HTML =======
        images_html = "\n".join([f'<img src="{url}" width="100%">' for url in product.get("images", [])])
        desc_html = "\n".join([f"<p>{p}</p>" for p in product.get("description", [])])
        features_html = "\n".join(
            [f'<p><b>{f.get("title","")}</b><br>{f.get("content","")}</p>' for f in product.get("features", [])]
        )
        highlights_html = "<br><br>\n".join(
            [f"{i+1}. {text}" for i, text in enumerate(product.get("highlights", []))]
        ) + "<br><br>"
        product_info_html = "\n".join(
            [f'<tr><th width="30%" bgcolor="#EEE">{p["name"]}</th><td bgcolor="#fff">{p["value"].replace("\n", "<br>")}</td></tr>'
            for p in product.get("product_info", [])]
        )

        # ======= 替換占位符 =======
        html_final = self.template
        html_final = html_final.replace("{{IMAGES}}", images_html)
        html_final = html_final.replace("{{DESCRIPTION}}", desc_html)
        html_final = html_final.replace("{{FEATURES}}", features_html)
        html_final = html_final.replace("{{HIGHLIGHTS}}", highlights_html)
        html_final = html_final.replace("{{PRODUCT_INFO}}", product_info_html)

        # ======= 輸出 HTML =======
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_final)
        print(f"HTML 已生成完成：{output_path}")
