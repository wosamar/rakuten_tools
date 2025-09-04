import streamlit as st
import pandas as pd

from database import Project, Shop
from handlers.database import DBHandler


# 將搜尋邏輯獨立成一個函式
def _fetch_shops_data(db: DBHandler, selected_project_name: str, shop_code: str, shop_name: str, all_projects: list):
    """
    根據搜尋條件從資料庫中獲取商店資料。
    """
    query_conditions = {}

    if selected_project_name == "全部":
        # 不添加任何 project_id 條件
        pass
    elif selected_project_name == "無專案":
        # 查詢 project_id 為空的商店
        query_conditions['project_id'] = None
    else:
        # 查詢特定專案名稱的商店
        project_id = next((p.id for p in all_projects if p.name == selected_project_name), None)
        if project_id:
            query_conditions['project_id'] = project_id

    if shop_code:
        query_conditions['name'] = shop_code

    if shop_name:
        query_conditions['display_name'] = shop_name

    if query_conditions:
        return db.get_all(Shop, **query_conditions)
    else:
        return db.get_all(Shop)


def shops_page():
    st.set_page_config(
        page_title="Shops",
        page_icon="🛍️",
        layout="wide",
    )

    st.title("🛍️ 商店資訊")
    st.write("---")

    db = DBHandler()

    all_projects = db.get_all(Project)
    project_names = ["全部", "無專案"] + [project.name for project in all_projects]

    # 查詢區塊
    with st.expander("商店查詢", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_project_name = st.selectbox("專案名", options=project_names)
        with col2:
            shop_code = st.text_input("商店代號", help="請輸入商店代號")
        with col3:
            shop_name = st.text_input("商店名", help="請輸入商店名稱")

        search_button = st.button("🔍 搜尋", type="primary")

    st.write("---")
    st.header("查詢結果")

    # 頁面載入時就執行一次無條件搜尋
    if 'search_results' not in st.session_state:
        st.session_state.search_results = _fetch_shops_data(db, "全部", "", "", all_projects)

    # 如果按鈕被點擊，就重新執行搜尋
    if search_button:
        st.session_state.search_results = _fetch_shops_data(db, selected_project_name, shop_code, shop_name,
                                                            all_projects)

    # 顯示結果
    results = st.session_state.search_results
    if results:
        data_to_display = []
        for shop in results:
            data_to_display.append({
                'id': shop.id,
                '專案名': shop.project.name,
                '商店代號': shop.name,
                '商店名': shop.display_name
            })

        df_shops = pd.DataFrame(data_to_display)
        st.dataframe(df_shops, use_container_width=True, hide_index=True)
    else:
        st.info("沒有找到符合條件的商店。")


if __name__ == '__main__':
    shops_page()
