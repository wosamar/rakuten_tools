from pathlib import Path
from typing import List

from env_settings import BASE_DIR
from scripts.items.models import ProductData, ProductDescription
from scripts.items.update_item_handler import ProductUpdater
from scripts.page_designs.enum import Template
from scripts.page_designs.excel_parser import ProductDocExtractor
from scripts.page_designs.html_generator import HTMLGenerator
from scripts.page_designs.utils import load_product_from_json
from utils import get_auth_token


def run(shop_code: str,
        input_dir: Path,  # for excel、json input
        output_dir: Path,  # for html output
        excel_name: str = None, product_names: List[str] = None,
        update_item: bool = True, is_test: bool = False):
    if not excel_name and not product_names:
        raise TypeError("Either excel_path or product_paths should be provided")

    # 讀 excel 並存成 json
    if excel_name:
        extractor = ProductDocExtractor(str(input_dir / "excel" / excel_name))
        product_names = extractor.to_json_files(out_dir=str(input_dir / "json"), shop_code=shop_code)

    # 設定各HTML template
    template_generators = {
        Template.PC_MAIN.value: HTMLGenerator(template_path=str(Template.PC_MAIN.path)),
        Template.PC_SUB.value: HTMLGenerator(template_path=str(Template.PC_SUB.path)),
        Template.MOBILE.value: HTMLGenerator(template_path=str(Template.MOBILE.path)),
    }

    product_updater = ProductUpdater(auth_token=get_auth_token())

    # 讀 Json 建 HTML
    for product_name in product_names:
        product = load_product_from_json(input_dir / "json" / product_name)
        for template_type, generator in template_generators.items():
            output_path = output_dir / f"{product.shop_code}-{product.product_id}-{template_type}"
            generator.generate_html(product.to_dict(), output_path=str(output_path))

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

            # TODO:錯誤處理
            print(product_updater.patch_item(product_data))

        if is_test:
            break


if __name__ == '__main__':
    shop_id = "tra-sonnac"
    in_dir = BASE_DIR / "input"
    out_dir = BASE_DIR / "output" / "html" / "sonnac"
    excel_n = "02_建治_商品資訊及文案_2025_雜.xlsx"
    product_ns = [
        # "tra-sonnac-01.json",
        # "tra-sonnac-02.json",
        # "tra-sonnac-03.json",
        # "tra-sonnac-04.json",
        "tra-sonnac-05.json",
    ]

    run(
        shop_id, in_dir, out_dir,
        # excel_name=excel_n,
        product_names=product_ns,
        # update_item=False,
        is_test=True
    )
