import streamlit as st
import pandas as pd

from database.models import Template
from handlers.database import DBHandler
from database import Shop, Product, Project


def _fetch_products_data(db: DBHandler, selected_shop_name: str, all_shops: list):
    """
    根據商店名從資料庫中獲取商品資料。
    """
    query_conditions = {}
    if selected_shop_name and selected_shop_name != "全部":
        shop_id = next((s.id for s in all_shops if s.name == selected_shop_name), None)
        if shop_id:
            query_conditions['shop_id'] = shop_id

    if query_conditions:
        return db.get_all(Product, **query_conditions)
    else:
        return db.get_all(Product)


def _fetch_template_info(db: DBHandler, type_id: int):
    query_conditions = {"template_type_id": type_id}

    return db.get_all(Template, **query_conditions)


def _generate_html_content(product_data, templates):
    """
    根據商品資料和模板選項，生成所有 HTML 內容。
    """
    pc_description_template, pc_sales_template, mobile_description_template = templates

    html_results = {}
    for _, row in product_data.iterrows():
        product_id = row['商品代號']

        # 假資料 HTML 內容
        html_code_pc_desc = f"\n<div style='border:1px solid gray; padding:10px;'>\n    <h1>{product_id}</h1>\n    <p>這是根據模板 {pc_description_template} 生成的PC用商品説明文。</p>\n</div>"
        html_code_pc_sales = f"\n<p>這是根據模板 {pc_sales_template} 生成的PC用販売説明文。</p>"
        html_code_mobile = f"\n<div style='background-color:#f0f0f0; padding:10px;'>\n    <h4>{product_id}</h4>\n    <p>這是根據模板 {mobile_description_template} 生成的行動裝置商品説明文。</p>\n</div>"

        # 將結果存入字典
        html_results[product_id] = {
            'pc_desc': html_code_pc_desc,
            'pc_sales': html_code_pc_sales,
            'mobile_desc': html_code_mobile
        }
    return html_results


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def tools_page():
    st.set_page_config(
        page_title="Tools",
        page_icon="🛠️",
        layout="wide",
    )

    st.title("🛠️ HTML 生成工具")
    st.write("---")

    db = DBHandler()

    all_shops = db.get_all(Shop)
    shop_names = ["全部"] + [shop.name for shop in all_shops]

    with st.expander("商品查詢與選擇", expanded=True):
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            selected_shop_name = st.selectbox("商店名", options=shop_names)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            search_button = st.button("🔍 搜尋", type="primary")

        if 'tools_search_results' not in st.session_state or search_button:
            st.session_state.tools_search_results = _fetch_products_data(db, selected_shop_name, all_shops)

    st.write("---")
    st.header("查詢結果")

    results = st.session_state.tools_search_results

    if results:
        data_to_display = []
        for product in results:
            data_to_display.append({
                "選擇": False,
                'id': product.id,
                '商品代號': product.manage_number,
                '商店名': product.shop.name if product.shop else "無商店",
            })

        df_products = pd.DataFrame(data_to_display)

        selected_df = st.data_editor(
            df_products,
            use_container_width=True,
            hide_index=True,
            column_config={
                "選擇": st.column_config.CheckboxColumn("選擇", help="勾選以生成 HTML", default=False),
                "id": st.column_config.Column("ID", disabled=True),
                "商品代號": st.column_config.Column("商品代號", disabled=True),
                "商店名": st.column_config.Column("商店名", disabled=True),
            },
            key="product_selector"
        )

        selected_products = pd.DataFrame()
        if '選擇' in selected_df.columns:
            selected_products = selected_df[selected_df['選擇'] == True]

        if not selected_products.empty:
            st.write("---")
            st.header("生成 HTML")

            template_col1, template_col2, template_col3 = st.columns(3)
            main_templates = _fetch_template_info(db, 1)
            sub_templates = _fetch_template_info(db, 2)
            mobile_templates = _fetch_template_info(db, 3)
            with template_col1:
                pc_description_template = st.selectbox(
                    "PC用商品説明文",
                    options=[t.name for t in main_templates]
                )
            with template_col2:
                pc_sales_template = st.selectbox(
                    "PC用販売説明文",
                    options=[t.name for t in sub_templates]
                )
            with template_col3:
                mobile_description_template = st.selectbox(
                    "スマートフォン用商品説明文",
                    options=[t.name for t in mobile_templates]
                )

            generate_html_button = st.button("生成 HTML", type="primary")

            if generate_html_button:
                st.write("---")
                st.subheader("HTML 生成結果")

                templates = (pc_description_template, pc_sales_template, mobile_description_template)
                html_results = _generate_html_content(selected_products, templates)

                # 為每個選定的商品建立一個分頁籤，使用商品代號作為標籤
                tabs = st.tabs([f"{row['商品代號']}" for _, row in selected_products.iterrows()])

                for i, (index, row) in enumerate(selected_products.iterrows()):
                    product_id = row['商品代號']
                    with tabs[i]:
                        st.markdown(f"**商品代號：** `{product_id}`")

                        with st.expander("PC用商品説明文", expanded=False):
                            st.code(html_results[product_id]['pc_desc'], language="html")
                            st.markdown(html_results[product_id]['pc_desc'], unsafe_allow_html=True)
                            st.text("\n")

                        with st.expander("PC用販売説明文", expanded=False):
                            st.code(html_results[product_id]['pc_sales'], language="html")
                            st.markdown(html_results[product_id]['pc_sales'], unsafe_allow_html=True)
                            st.text("\n")

                        with st.expander("スマートフォン用商品説明文", expanded=False):
                            st.code(html_results[product_id]['mobile_desc'], language="html")
                            st.markdown(html_results[product_id]['mobile_desc'], unsafe_allow_html=True)
                            st.text("\n")

        else:
            st.info("請在表格中勾選商品，然後進行操作。")
    else:
        st.info("沒有找到符合條件的商品。")


if __name__ == "__main__":
    tools_page()
