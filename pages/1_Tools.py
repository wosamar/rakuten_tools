from copy import copy

import streamlit as st

from env_settings import EnvSettings
from handlers.excel_parser import ProductExcelParser
from handlers.html_generator import HTMLGenerator
from handlers.item_handler import ItemHandler
from models.item import ProductData, ProductDescription
from models.product_descript import ProductDescriptionData

env_settings = EnvSettings()

html_display_names = {
    "pc_main": "PC用商品説明文",
    "pc_sub": "PC用販売説明文",
    "mobile": "スマートフォン用商品説明文"
}


def generate_htmls(product):
    pc_main_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "pc-main.html"))
    pc_sub_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "pc-sub.html"))
    mobile_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "mobile.html"))

    return {
        'pc_main': pc_main_gen.generate_html(product),
        'pc_sub': pc_sub_gen.generate_html(product),
        'mobile': mobile_gen.generate_html(product)
    }


def show_htmls(store_id: str, product_datas: list):
    tab_titles = [f"{store_id}-{product_data["sequence"]}" for product_data in product_datas]
    tabs = st.tabs(tab_titles)

    p_html_dict = {}  # for 後台更新作業
    for i, product_data in enumerate(product_datas):
        parse_data = copy(product_data)
        with tabs[i]:
            manage_number = tab_titles[i]
            st.subheader(f"商品編號：{manage_number}")

            parse_data.pop("sequence")
            parse_data["shop_code"] = store_id
            htmls = generate_htmls(ProductDescriptionData(**parse_data))

            for label, content in htmls.items():
                with st.expander(html_display_names.get(label), expanded=False):
                    st.code(content, language="html")
                    # st.markdown(content, unsafe_allow_html=True)

            st.success(f"商品 {manage_number} 的 HTML 已成功生成！")

        p_html_dict.update({manage_number: htmls})

    return p_html_dict


def show_page():
    st.set_page_config(
        page_title="Excel 轉 HTML 工具",
        page_icon="📄",
        layout="wide"
    )
    st.title("Excel 轉 HTML 小工具")

    # --- 輸入區塊 ---
    st.subheader("輸入設定")

    store_id = st.text_input("商店代號", help="請輸入商店代碼，例如：tra-demo")
    uploaded_file = st.file_uploader("請上傳 Excel 檔案", type=["xlsx", "xls"], help="僅支援 .xlsx 或 .xls 格式")

    # --- 功能按鈕區塊 ---
    if 'p_html_dict' not in st.session_state:
        st.session_state.p_html_dict = None

    if st.button("生成 HTML"):
        st.write("---")
        # 檢查輸入是否齊全
        if not store_id:
            st.error("請先輸入商店代號！")
        elif not uploaded_file:
            st.error("請先上傳 Excel 檔案！")
        else:
            # 使用 st.spinner 顯示載入中
            with st.spinner('正在轉換中...'):
                # 實例化解析器並解析所有工作表
                parser = ProductExcelParser(excel_bytes=uploaded_file.getvalue())
                product_datas = parser.parse_all_sheets()

                if not product_datas:
                    st.warning("Excel 檔案中未找到任何符合解析格式的工作表。")
                else:
                    st.session_state.p_html_dict = show_htmls(store_id, product_datas)

    # --- 後台更新按鈕區塊 ---
    st.write("---")
    st.subheader("更新至後台")
    item_handler = ItemHandler(env_settings.auth_token)
    if st.button("將 HTML 直接更新至後台"):
        if not st.session_state.p_html_dict:
            st.warning("請先上傳 Excel 檔案，並生成 HTML")
        else:
            for manage_number, htmls in st.session_state.p_html_dict.items():
                product_data = ProductData(
                    manage_number=manage_number,
                    product_description=ProductDescription(
                        pc=htmls.get("pc_main"),
                        sp=htmls.get("mobile"),
                    ),
                    sales_description=htmls.get("pc_sub"),
                )
                item_handler.patch_item(product_data)

                st.success(f"商品 {manage_number} 已成功更新！")
                st.markdown(f"**預覽連結：**")
                st.markdown(f"- [PC 預覽](https://soko.rms.rakuten.co.jp/{env_settings.TENPO_NAME}/{manage_number}/)")
                st.markdown(f"- [行動版預覽](https://soko.rms.rakuten.co.jp/{env_settings.TENPO_NAME}/{manage_number}/?force-site=ipn)")

    st.markdown("""
    <style>
        .stButton>button {
            font-size: 1.2rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    show_page()
