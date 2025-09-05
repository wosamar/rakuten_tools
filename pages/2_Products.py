import streamlit as st
import pandas as pd
from database import Shop, Product
from handlers.database import DBHandler

db = DBHandler()  # 全局共用 DBHandler

# ----------------- 查詢函式 -----------------
def fetch_products(selected_shop_name: str, all_shops: list):
    query_conditions = {}
    if selected_shop_name and selected_shop_name != "全部":
        shop_id = next((s.id for s in all_shops if s.name == selected_shop_name), None)
        if shop_id:
            query_conditions['shop_id'] = shop_id
    return db.get_all(Product, **query_conditions) if query_conditions else db.get_all(Product)

# ----------------- Tab 函式 -----------------
def product_list_tab():
    st.header("📦 商品列表")
    all_shops = db.get_all(Shop)
    shop_names = ["全部"] + [shop.name for shop in all_shops]

    with st.expander("商品查詢", expanded=True):
        selected_shop_name = st.selectbox("商店名", shop_names)
        search_button = st.button("🔍 搜尋", key="search_list")

    if 'product_search_results' not in st.session_state or search_button:
        st.session_state.product_search_results = fetch_products(selected_shop_name, all_shops)

    results = st.session_state.product_search_results
    if results:
        df = pd.DataFrame([{
            'id': p.id,
            '商品代號': p.manage_number,
            '商店名': p.shop.name if p.shop else "無商店",
            '商品描述': p.description,
            '商品簡述': p.feature,
            '商品特色': p.highlight,
            '商品資訊': p.info
        } for p in results])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("沒有找到符合條件的商品。")

def add_product_tab():
    st.header("📤 新增商品")
    all_shops = db.get_all(Shop)
    with st.form("add_products_form"):
        selected_shop_name = st.selectbox("選擇商店", [""] + [shop.name for shop in all_shops])
        excel_file = st.file_uploader("上傳商品 Excel 檔案", type=["xlsx", "xls"])
        submitted = st.form_submit_button("新增商品")

        if submitted:
            if not selected_shop_name:
                st.error("請選擇商店")
            elif not excel_file:
                st.error("請上傳 Excel 檔案")
            else:
                shop = next((s for s in all_shops if s.name == selected_shop_name), None)
                if not shop:
                    st.error("商店不存在")
                else:
                    df = pd.read_excel(excel_file)
                    db_count = 0
                    for _, row in df.iterrows():
                        new_product = Product(
                            manage_number=row.get("商品代號"),
                            description=row.get("商品描述", ""),
                            feature=row.get("商品簡述", ""),
                            highlight=row.get("商品特色", ""),
                            info=row.get("商品資訊", ""),
                            shop_id=shop.id
                        )
                        db.add(new_product)
                        db_count += 1
                    st.success(f"成功新增 {db_count} 筆商品到 {shop.name}")

def edit_product_tab():
    st.header("✏️ 編輯商品")
    all_shops = db.get_all(Shop)
    shop_names = [shop.name for shop in all_shops]

    selected_shop_name = st.selectbox("選擇商店", shop_names)
    if ('last_shop' not in st.session_state) or (st.session_state.last_shop != selected_shop_name):
        st.session_state.edit_product_results = fetch_products(selected_shop_name, all_shops)
        st.session_state.last_shop = selected_shop_name

    results = st.session_state.edit_product_results
    if results:
        product_options = {p.manage_number: p for p in results}
        selected_number = st.selectbox("選擇商品編號", [""] + list(product_options.keys()))
        if selected_number:
            product = product_options[selected_number]

            st.text_area("商品描述", product.description, height=200)
            st.text_area("商品簡述", product.feature, height=160)
            st.text_area("商品特色", product.highlight, height=160)

            # JSON / 表格編輯商品資訊
            st.text("商品資訊")
            info_dict = product.info_dict if isinstance(product.info_dict, dict) else {}
            info_df = pd.DataFrame(info_dict.items(), columns=["項目", "內容"])
            edited_df = st.data_editor(info_df, use_container_width=True, height=300)
            edited_info = dict(zip(edited_df["項目"], edited_df["內容"]))

            if st.button("💾 儲存修改"):
                product.info_dict = edited_info  # setter 會自動轉 JSON
                db.update(product)
                st.success(f"商品 {product.manage_number} 修改成功！")
    else:
        st.info("沒有找到符合條件的商品。")


# ----------------- 主頁 -----------------
def products_page():
    st.set_page_config(page_title="Products", page_icon="📦", layout="wide")
    st.title("📦 商品管理")
    st.write("---")

    tabs = st.tabs(["商品列表", "新增商品", "修改商品"])
    with tabs[0]:
        product_list_tab()
    with tabs[1]:
        add_product_tab()
    with tabs[2]:
        edit_product_tab()

if __name__ == "__main__":
    products_page()
