from typing import List

from env_settings import EnvSettings
from handlers.excel_parser import ProductDocExtractor

env_settings = EnvSettings()


def run(shop_id: int,
        excel_file: str = None, products: List[str] = None,
        update_item: bool = True, is_test: bool = False):
    if not excel_file and not products:
        raise TypeError("Either excel_path or product_paths should be provided")

    # 讀 excel 並存成 json
    if excel_file:
        extractor = ProductDocExtractor(shop_id, excel_path=str(env_settings.excel_dir / excel_file))
        products = extractor.process_excel_to_db()

    # # 設定各HTML template
    # template_generators = {
    #     Template.PC_MAIN.value: HTMLGenerator(template_path=str(Template.PC_MAIN.path)),
    #     Template.PC_SUB.value: HTMLGenerator(template_path=str(Template.PC_SUB.path)),
    #     Template.MOBILE.value: HTMLGenerator(template_path=str(Template.MOBILE.path)),
    # }
    #
    # output_dir = env_settings.html_dir / shop_name
    # item_handler = ItemHandler(auth_token=env_settings.auth_token)
    #
    # # 讀 Json 建 HTML
    # for json_name in products:
    #     product = ProductDescriptionData.from_json(env_settings.json_dir / shop_name / json_name)
    #     for template_type, generator in template_generators.items():
    #         file_name = f"{product.shop_code}-{product.product_id}-{template_type}"
    #         generator.generate_html(product.to_dict(), out_dir=str(output_dir), file_name=file_name)
    #
    #     # 更新至樂天後台
    #     if update_item:
    #         item_manage_number = f"{product.shop_code}-{product.product_id}"
    #         product_data = ProductData(
    #             manage_number=item_manage_number,
    #         )
    #
    #         # 把 HTML 讀進來塞到對應欄位
    #         pc_html = (output_dir / f"{product.shop_code}-{product.product_id}-{Template.PC_MAIN.value}").read_text(
    #             encoding="utf-8")
    #         sp_html = (output_dir / f"{product.shop_code}-{product.product_id}-{Template.MOBILE.value}").read_text(
    #             encoding="utf-8")
    #         sales_html = (output_dir / f"{product.shop_code}-{product.product_id}-{Template.PC_SUB.value}").read_text(
    #             encoding="utf-8")
    #
    #         product_data.product_description = ProductDescription(pc=pc_html, sp=sp_html)
    #         product_data.sales_description = sales_html
    #
    #         resp = item_handler.patch_item(product_data)
    #         if resp.status_code != 204:
    #             raise Exception(resp.status_code, resp.text)
    #
    #     if is_test:
    #         break


# 從excel建立/更新商品
def create_product_from_doc(shop_id: int, file_path: str):
    extractor = ProductDocExtractor(
        shop_id, excel_path=file_path
    )
    return extractor.process_excel_to_db()


# 查詢商品資訊
# 修改商品資訊
# 產出HTML並更新至樂天後台（可選）

if __name__ == '__main__':
    doc_path = str(env_settings.excel_dir / "tra-sonnac.xlsx")
    create_product_from_doc(1,doc_path)

    # shop_n = "tra-sonnac"
    # excel_n = "tra-sonnac.xlsx"
    # json_ns = [
    #     "tra-sonnac-01.json",
    #     "tra-sonnac-02.json",
    #     "tra-sonnac-03.json",
    #     "tra-sonnac-04.json",
    #     "tra-sonnac-05.json",
    # ]
    #
    # run(
    #     1,
    #     excel_file=excel_n,
    #     # json_files=json_ns,
    #     # update_item=False,
    #     # is_test=True
    # )
