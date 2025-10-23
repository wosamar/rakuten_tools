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


def clear_p_html_dict():
    if "p_html_dict" in st.session_state:
        st.session_state.p_html_dict = {}


def generate_htmls(product):
    pc_main_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "pc-main.html"))
    pc_sub_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "pc-sub.html"))
    mobile_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "mobile.html"))

    return {
        'pc_main': pc_main_gen.generate_html(product),
        'pc_sub': pc_sub_gen.generate_html(product),
        'mobile': mobile_gen.generate_html(product, is_mobile=True)
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
                html_display_name = html_display_names.get(label)
                with st.expander(html_display_name, expanded=False):
                    st.code(content, language="html")

                with st.expander(f"{html_display_name}（預覽）", expanded=False):
                    st.markdown(content, unsafe_allow_html=True)

            st.success(f"商品 {manage_number} 的 HTML 已成功生成！")

        p_html_dict.update({manage_number: htmls})

    return p_html_dict


def update_item_and_show_result(item_handler, manage_number, htmls):
    product_data = ProductData(
        manage_number=manage_number,
        product_description=ProductDescription(
            pc=htmls.get("pc_main"),
            sp=htmls.get("mobile"),
        ),
        sales_description=htmls.get("pc_sub"),
    )
    try:
        item_handler.patch_item(manage_number, product_data.to_patch_payload())
    except Exception as e:
        st.error(f"商品 {manage_number} 更新失敗，錯誤訊息：{e}")
    else:
        st.success(f"商品 {manage_number} 已成功更新！")
        if hasattr(env_settings, "TENPO_NAME"):
            pc_preview_url = f"https://soko.rms.rakuten.co.jp/{env_settings.TENPO_NAME}/{manage_number}/"
            mobile_preview_url = f"https://soko.rms.rakuten.co.jp/{env_settings.TENPO_NAME}/{manage_number}/?force-site=ipn"
            st.markdown(f"**預覽連結：**")
            st.markdown(
                f"- [PC 預覽]({pc_preview_url})"
            )
            st.markdown(
                f"- [手機預覽]({mobile_preview_url})"
            )


def show_page():
    st.set_page_config(
        page_title="Excel 轉 HTML 工具",
        page_icon="📄",
        layout="wide"
    )
    st.title("Excel 轉 HTML 小工具")

    # --- 輸入區塊 ---
    st.subheader("輸入設定")

    store_id = st.text_input("商店代號", help="請輸入商店代碼，例如：tra-demo", on_change=clear_p_html_dict)
    uploaded_file = st.file_uploader("請上傳 Excel 檔案", type=["xlsx", "xls"], help="僅支援 .xlsx 或 .xls 格式")

    # --- 功能按鈕區塊 ---
    if 'p_html_dict' not in st.session_state:
        st.session_state.p_html_dict = {}

    if 'items_checked' not in st.session_state:
        st.session_state.items_checked = {}

    if st.button("生成 HTML"):
        st.write("---")

        st.session_state.items_checked = {}  # 重置已勾選項目
        if not store_id:
            st.error("請先輸入商店代號！")
        elif not uploaded_file:
            st.error("請先上傳 Excel 檔案！")
        else:
            # 使用 st.spinner 顯示載入中
            with st.spinner('正在轉換中...'):
                # 實例化解析器並解析所有工作表
                parser = ProductExcelParser(store_id, excel_bytes=uploaded_file.getvalue())
                product_datas = parser.parse_all_sheets()

                if not product_datas:
                    st.warning("Excel 檔案中未找到任何符合解析格式的工作表。")
                else:
                    st.session_state.p_html_dict = show_htmls(store_id, product_datas)

    # --- 後台更新按鈕區塊 ---
    st.write("---")
    st.subheader("更新至後台")

    if not st.session_state.p_html_dict:
        st.warning("請先上傳 Excel 檔案，並生成 HTML")
    else:
        item_handler = ItemHandler(env_settings.auth_token)
        manage_numbers = list(st.session_state.p_html_dict.keys())

        @st.dialog("確認更新", width="small")
        def confirm_update_dialog(items_to_update):
            st.warning(f"您確定要更新所選的 {len(items_to_update)} 個商品嗎？此操作無法復原。")

            confirm_cols = st.columns([1, 1, 1, 1])
            with confirm_cols[1]:
                btn = st.button("確定更新", type="primary")
            if btn:
                st.session_state.items_to_update = items_to_update
                st.rerun()

            with confirm_cols[2]:
                if st.button("取消", type="secondary"):
                    st.rerun()  # 點擊取消後，重新執行腳本以關閉視窗

            # 初始化 session_state 來追蹤勾選狀態
            if "items_checked" not in st.session_state:
                st.session_state.items_checked = {num: False for num in manage_numbers}

        # --- 真正的更新邏輯區塊 ---
        if "items_to_update" in st.session_state and st.session_state.items_to_update:
            with st.spinner('正在更新所選商品...'):
                for manage_number in st.session_state.items_to_update:
                    update_item_and_show_result(
                        item_handler, manage_number,
                        st.session_state.p_html_dict[manage_number]
                    )

            del st.session_state.items_to_update
            st.markdown("---")

        def update_single_checkbox(m_number):
            st.session_state.items_checked[m_number] = st.session_state[f"checkbox_{m_number}"]

        def update_all_checkboxes(select_all):
            for num in manage_numbers:
                st.session_state.items_checked[num] = select_all

        # 全選與取消全選按鈕
        cols = st.columns([1, 5])
        with cols[0]:
            if st.button("全選"):
                update_all_checkboxes(True)
            if st.button("取消全選"):
                update_all_checkboxes(False)

        # 個別勾選的清單
        with cols[1]:
            for manage_number in manage_numbers:
                st.checkbox(
                    f"**{manage_number}**",
                    value=st.session_state.items_checked.get(manage_number, False),
                    key=f"checkbox_{manage_number}",
                    on_change=update_single_checkbox,
                    args=(manage_number,)
                )
        # --- 執行按鈕 ---
        st.markdown("---")
        selected_items = [num for num, checked in st.session_state.items_checked.items() if checked]
        if st.button(f"更新所選項目 ({len(selected_items)})", disabled=not selected_items):
            if selected_items:
                confirm_update_dialog(selected_items)

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
