import streamlit as st
import pandas as pd
from database import Shop, Product
from handlers.database import DBHandler


# 將商品搜尋邏輯獨立成一個函式
def _fetch_products_data(db: DBHandler, selected_shop_name: str, all_shops: list):
    """
    根據商店名從資料庫中獲取商品資料。
    """
    query_conditions = {}
    if selected_shop_name and selected_shop_name != "全部":
        # 找到對應商店的 ID
        shop_id = next((s.id for s in all_shops if s.name == selected_shop_name), None)
        if shop_id:
            query_conditions['shop_id'] = shop_id

    # 執行查詢並返回結果
    if query_conditions:
        return db.get_all(Product, **query_conditions)
    else:
        return db.get_all(Product)


def products_page():
    st.set_page_config(
        page_title="Products",
        page_icon="📦",
        layout="wide",
    )

    st.title("📦 商品資訊")
    st.write("---")

    db = DBHandler()

    # 獲取所有商店名稱
    all_shops = db.get_all(Shop)
    shop_names = ["全部"] + [shop.name for shop in all_shops]

    # 使用 st.expander 將查詢區塊收合
    with st.expander("商品查詢", expanded=True):
        selected_shop_name = st.selectbox("商店名", options=shop_names)
        search_button = st.button("🔍 搜尋", type="primary")

    st.write("---")
    st.header("查詢結果")

    # 頁面載入時或按鈕被點擊時執行搜尋
    if 'product_search_results' not in st.session_state or search_button:
        st.session_state.product_search_results = _fetch_products_data(db, selected_shop_name, all_shops)

    # 顯示結果
    results = st.session_state.product_search_results
    if results:
        data_to_display = []
        for product in results:
            data_to_display.append({
                'id': product.id,
                '商品代號': product.manage_number,
                '商店名': product.shop.name if product.shop else "無商店",
                '商品描述': product.description,
                '商品簡述': product.feature,
                '商品特色': product.highlight,
                '商品資訊': product.info
            })

        df_products = pd.DataFrame(data_to_display)
        st.dataframe(df_products, use_container_width=True, hide_index=True)
    else:
        st.info("沒有找到符合條件的商品。")


if __name__ == "__main__":
    products_page()