from copy import copy

import streamlit as st

from env_settings import EnvSettings
from handlers.excel_parser import ProductExcelParser
from handlers.html_generator import HTMLGenerator
from models.product_descript import ProductDescriptionData

env_settings = EnvSettings()


def generate_htmls(product):
    pc_desc_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "pc-main.html"))
    pc_sales_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "pc-sub.html"))
    mobile_gen = HTMLGenerator(str(env_settings.html_tmp_dir / "mobile.html"))

    return {
        'PC用商品説明文': pc_desc_gen.generate_html(product),
        'PC用販売説明文': pc_sales_gen.generate_html(product),
        'スマートフォン用商品説明文': mobile_gen.generate_html(product)
    }


st.set_page_config(
    page_title="Excel 轉 HTML 工具",
    page_icon="📄",
    layout="wide"
)

# 頁面標題
st.title("Excel 轉 HTML 小工具")

# --- 輸入區塊 ---
st.subheader("輸入設定")

store_id = st.text_input("商店代號", help="請輸入商店代碼，例如：A123")
uploaded_file = st.file_uploader("請上傳 Excel 檔案", type=["xlsx", "xls"], help="僅支援 .xlsx 或 .xls 格式")

# --- 功能按鈕區塊 ---

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
                # 取得工作表名稱作為分頁標題
                tab_titles = [f"{store_id}-{product_data["sequence"]}" for product_data in product_datas]

                # 創建分頁
                tabs = st.tabs(tab_titles)

                for i, product_data in enumerate(product_datas):
                    parse_data = copy(product_data)
                    with tabs[i]:
                        manage_number = tab_titles[i]
                        st.subheader(f"商品編號：{manage_number}")

                        parse_data.pop("sequence")
                        parse_data["shop_code"] = store_id
                        htmls = generate_htmls(ProductDescriptionData(**parse_data))

                        for label, content in htmls.items():
                            with st.expander(label, expanded=False):
                                st.code(content, language="html")
                                st.markdown(content, unsafe_allow_html=True)

                        st.success(f"商品 {manage_number} 的 HTML 已成功生成！")


# --- 後台更新按鈕區塊 (此為範例，實際邏輯需自行實作) ---
st.write("---")
st.subheader("更新至後台")
if st.button("將 HTML 直接更新至後台"):
    # 這裡可以放置你的後台更新邏輯
    # 例如：調用 API 或執行腳本
    st.info("此功能尚未實作，請在此處加入你的後台更新邏輯。")

st.markdown("""
<style>
    .stButton>button {
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)
