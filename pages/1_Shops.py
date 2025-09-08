import streamlit as st
import pandas as pd
from database import Project, Shop
from handlers.database import DBHandler

def _fetch_shops_data(db: DBHandler, selected_project_name: str, shop_code: str, shop_name: str, all_projects: list):
    """根據搜尋條件從資料庫中獲取商店資料"""
    query_conditions = {}

    if selected_project_name == "全部":
        pass
    elif selected_project_name == "無專案":
        query_conditions['project_id'] = None
    else:
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

# ----------------- 三個 Tab 函式 -----------------

def list_shops_tab(db: DBHandler, all_projects: list):
    st.header("商店查詢 / 列表")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_project_name = st.selectbox("專案名", ["全部", "無專案"] + [p.name for p in all_projects])
    with col2:
        shop_code = st.text_input("商店代號")
    with col3:
        shop_name = st.text_input("商店名稱")
    search_button = st.button("🔍 搜尋")

    if 'search_results' not in st.session_state or search_button:
        st.session_state.search_results = _fetch_shops_data(db, selected_project_name, shop_code, shop_name, all_projects)

    results = st.session_state.search_results
    if results:
        df = pd.DataFrame([{'id': s.id, '專案名': s.project.name if s.project else "無專案",
                            '商店代號': s.name, '商店名': s.display_name} for s in results])
        st.dataframe(df, width='stretch', hide_index=True)
    else:
        st.info("沒有找到符合條件的商店。")

def add_shop_tab(db: DBHandler, all_projects: list):
    st.header("新增商店")
    with st.form("add_shop_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_shop_code = st.text_input("商店代號")
        with col2:
            new_shop_name = st.text_input("商店名稱")
        with col3:
            new_project_name = st.selectbox("專案", ["無專案"] + [p.name for p in all_projects])
        submitted = st.form_submit_button("新增商店")
        if submitted:
            project_id = None
            if new_project_name != "無專案":
                project = next((p for p in all_projects if p.name == new_project_name), None)
                project_id = project.id if project else None
            new_shop = Shop(name=new_shop_code, display_name=new_shop_name, project_id=project_id)
            db.add(new_shop)
            st.success(f"商店 {new_shop_name} 新增成功！請重新查詢。")

def edit_shop_tab(db: DBHandler, all_projects: list):
    st.header("修改商店")
    results = db.get_all(Shop)
    shop_names = [s.display_name for s in results]
    selected_name = st.selectbox("選擇要修改的商店", [""] + shop_names)
    if selected_name:
        shop = next((s for s in results if s.display_name == selected_name), None)
        if shop:
            with st.form("edit_shop_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_code = st.text_input("商店代號", value=shop.name)
                with col2:
                    new_name = st.text_input("商店名稱", value=shop.display_name)
                with col3:
                    project_options = ["無專案"] + [p.name for p in all_projects]
                    new_project_name = st.selectbox("專案", project_options, index=0 if not shop.project else project_options.index(shop.project.name))
                submitted = st.form_submit_button("修改商店")
                if submitted:
                    shop.name = new_code
                    shop.display_name = new_name
                    if new_project_name == "無專案":
                        shop.project_id = None
                    else:
                        project = next((p for p in all_projects if p.name == new_project_name), None)
                        shop.project_id = project.id if project else None
                    db.add(shop)  # 更新資料庫
                    st.success(f"商店 {new_name} 修改成功！請重新查詢。")

# ----------------- 主頁 -----------------

def shops_page():
    st.set_page_config(page_title="Shops", page_icon="🛍️", layout="wide")
    st.title("🛍️ 商店管理")
    st.write("---")

    db = DBHandler()
    all_projects = db.get_all(Project)

    tabs = st.tabs(["列表 / 查詢", "新增商店", "修改商店"])
    with tabs[0]:
        list_shops_tab(db, all_projects)
    with tabs[1]:
        add_shop_tab(db, all_projects)
    with tabs[2]:
        edit_shop_tab(db, all_projects)

if __name__ == "__main__":
    shops_page()
