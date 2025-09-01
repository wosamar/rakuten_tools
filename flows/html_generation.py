from pathlib import Path
from typing import List

from env_settings import BASE_DIR
from items.models import ProductData, ProductDescription
from items.update_item_handler import ProductUpdater
from page_designs.enum import Template
from page_designs.excel_parser import ProductDocExtractor
from page_designs.html_generator import HTMLGenerator
from page_designs.utils import load_product_from_json
from utils import get_auth_token


def run(shop_code: str, work_dir: Path,  # for excel、json、html input and output
        excel_name: str = None, product_names: List[str] = None,
        update_item: bool = True, is_test: bool = False):
    if not excel_name and not product_names:
        raise TypeError("Either excel_path or product_paths should be provided")

    # 讀 excel 並存成 json
    if excel_name:
        extractor = ProductDocExtractor(str(work_dir / excel_name))
        product_names = extractor.to_json_files(str(work_dir), shop_code=shop_code)

    # productDescription - pc = Template.PC_MAIN.value
    # productDescription - sp = Template.PC_SUB.value
    # salesDescription = Template.PC_SUB.value

    # 設定各HTML template
    template_generators = {
        Template.PC_MAIN.value: HTMLGenerator(template_path=str(Template.PC_MAIN.path)),
        Template.PC_SUB.value: HTMLGenerator(template_path=str(Template.PC_SUB.path)),
        Template.MOBILE.value: HTMLGenerator(template_path=str(Template.MOBILE.path)),
    }

    product_updater = ProductUpdater(auth_token=get_auth_token())

    # 讀 Json 建 HTML
    for product_name in product_names:
        product = load_product_from_json(work_dir / product_name)
        for template_type, generator in template_generators.items():
            output_path = work_dir / f"{product.shop_code}-{product.product_id}-{template_type}"
            generator.generate_html(product.to_dict(), output_path=str(output_path))

        if update_item:
            item_manage_number = f"{product.shop_code}-{product.product_id}"
            product_data = ProductData(
                manage_number=item_manage_number,
            )

            # 把 HTML 讀進來塞到對應欄位
            pc_html = (work_dir / f"{product.shop_code}-{product.product_id}-{Template.PC_MAIN.value}").read_text(
                encoding="utf-8")
            sp_html = (work_dir / f"{product.shop_code}-{product.product_id}-{Template.MOBILE.value}").read_text(
                encoding="utf-8")
            sales_html = (work_dir / f"{product.shop_code}-{product.product_id}-{Template.PC_SUB.value}").read_text(
                encoding="utf-8")

            product_data.product_description = ProductDescription(pc=pc_html, sp=sp_html)
            product_data.sales_description = sales_html

            print(product_updater.patch_item(product_data))

        if is_test:
            break


if __name__ == '__main__':
    shop_id = "tra-sonnac"
    out_dir = BASE_DIR / "page_designs" / "output" / "sonnac"
    excel_n = "02_建治_商品資訊及文案_2025_雜.xlsx"
    product_ns = [
        # "tra-sonnac-01.json",
        # "tra-sonnac-02.json",
        # "tra-sonnac-03.json",
        # "tra-sonnac-04.json",
        "tra-sonnac-05.json",
    ]

    run(
        shop_id, out_dir,
        # excel_name=excel_n,
        product_names=product_ns,
        # update_item=False,
        is_test=True
    )
