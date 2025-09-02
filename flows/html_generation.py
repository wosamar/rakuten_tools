from pathlib import Path
from typing import List

from env_settings import EnvSettings
from scripts.items.item_handler import ItemHandler
from scripts.items.models import ProductData, ProductDescription
from scripts.page_designs.enum import Template
from scripts.page_designs.excel_parser import ProductDocExtractor
from scripts.page_designs.html_generator import HTMLGenerator
from scripts.page_designs.models import ProductDescriptionData
from utils import get_auth_token

env_settings = EnvSettings()


def run(shop_name: str,
        excel_name: str = None, product_names: List[str] = None,
        update_item: bool = True, is_test: bool = False):
    if not excel_name and not product_names:
        raise TypeError("Either excel_path or product_paths should be provided")

    # 讀 excel 並存成 json
    if excel_name:
        extractor = ProductDocExtractor(shop_name, excel_path=str(env_settings.excel_dir / excel_name))
        product_names = extractor.to_json_files(out_dir=str(env_settings.json_dir / shop_name))

    # 設定各HTML template
    template_generators = {
        Template.PC_MAIN.value: HTMLGenerator(template_path=str(Template.PC_MAIN.path)),
        Template.PC_SUB.value: HTMLGenerator(template_path=str(Template.PC_SUB.path)),
        Template.MOBILE.value: HTMLGenerator(template_path=str(Template.MOBILE.path)),
    }

    output_dir = env_settings.html_dir / shop_name
    item_handler = ItemHandler(auth_token=get_auth_token())

    # 讀 Json 建 HTML
    for product_name in product_names:
        product = ProductDescriptionData.from_json(env_settings.json_dir / shop_name / product_name)
        for template_type, generator in template_generators.items():
            file_name = f"{product.shop_code}-{product.product_id}-{template_type}"
            generator.generate_html(product.to_dict(), out_dir=str(output_dir), file_name=file_name)

        # 更新至樂天後台
        if update_item:
            item_manage_number = f"{product.shop_code}-{product.product_id}"
            product_data = ProductData(
                manage_number=item_manage_number,
            )

            # 把 HTML 讀進來塞到對應欄位
            pc_html = (output_dir / f"{product.shop_code}-{product.product_id}-{Template.PC_MAIN.value}").read_text(
                encoding="utf-8")
            sp_html = (output_dir / f"{product.shop_code}-{product.product_id}-{Template.MOBILE.value}").read_text(
                encoding="utf-8")
            sales_html = (output_dir / f"{product.shop_code}-{product.product_id}-{Template.PC_SUB.value}").read_text(
                encoding="utf-8")

            product_data.product_description = ProductDescription(pc=pc_html, sp=sp_html)
            product_data.sales_description = sales_html

            resp = item_handler.patch_item(product_data)
            if resp != 204:
                raise Exception(resp.status_code, resp.text)

        if is_test:
            break


if __name__ == '__main__':
    shop_n = "tra-sonnac"
    excel_n = "tra-sonnac.xlsx"
    product_ns = [
        "tra-sonnac-01.json",
        "tra-sonnac-02.json",
        "tra-sonnac-03.json",
        "tra-sonnac-04.json",
        "tra-sonnac-05.json",
    ]

    run(
        shop_n,
        excel_name=excel_n,
        # product_names=product_ns,
        update_item=False,
        is_test=True
    )
