import streamlit as st
import pandas as pd

from database.models import Shop, Product, Template
from env_settings import EnvSettings
from handlers.database import DBHandler
from handlers.html_generator import HTMLGenerator

env_settings = EnvSettings()


def fetch_products(db: DBHandler, selected_shop_name: str, all_shops: list):
    query = {}
    if selected_shop_name and selected_shop_name != "全部":
        shop = next((s for s in all_shops if s.name == selected_shop_name), None)
        if shop:
            query['shop_id'] = shop.id
    return db.get_all(Product, **query) if query else db.get_all(Product)


def fetch_templates(db: DBHandler, template_type_id: int):
    return db.get_all(Template, template_type_id=template_type_id)


def generate_html(product, pc_desc_tpl, pc_sales_tpl, mobile_tpl):
    pc_desc_gen = HTMLGenerator(str(env_settings.html_tmp_dir / pc_desc_tpl.path))
    pc_sales_gen = HTMLGenerator(str(env_settings.html_tmp_dir / pc_sales_tpl.path))
    mobile_gen = HTMLGenerator(str(env_settings.html_tmp_dir / mobile_tpl.path))

    return {
        'pc_desc': pc_desc_gen.generate_html(product),
        'pc_sales': pc_sales_gen.generate_html(product),
        'mobile': mobile_gen.generate_html(product)
    }


def tools_page():
    st.set_page_config(page_title="Tools", page_icon="🛠️", layout="wide")
    st.title("🛠️ HTML 生成工具")
    st.write("---")

    db = DBHandler()
    all_shops = db.get_all(Shop)
    shop_names = ["全部"] + [s.name for s in all_shops]

    # 查詢
    selected_shop = st.selectbox("商店名", shop_names)
    products = fetch_products(db, selected_shop, all_shops)

    if not products:
        st.info("沒有找到符合條件的商品。")
        return

    # 顯示商品選擇
    data = [{'選擇': False, '商品代號': p.manage_number, '商店名': p.shop.name if p.shop else "無商店"} for p in
            products]
    df = pd.DataFrame(data)
    selected_df = st.data_editor(df, use_container_width=True, hide_index=True,
                                 column_config={'選擇': st.column_config.CheckboxColumn('選擇', default=False)})
    selected_products = [products[i] for i, checked in enumerate(selected_df['選擇']) if checked]

    if not selected_products:
        st.info("請勾選商品後再操作。")
        return

    st.write("---")
    st.header("選擇模板")
    pc_desc_tpl = st.selectbox(
        "PC用商品説明文",
        options=fetch_templates(db, 1),
        format_func=lambda t: t.name  # 顯示模板名稱
    )
    pc_sales_tpl = st.selectbox(
        "PC用販売説明文",
        options=fetch_templates(db, 2),
        format_func=lambda t: t.name
    )
    mobile_tpl = st.selectbox(
        "スマートフォン用商品説明文",
        options=fetch_templates(db, 3),
        format_func=lambda t: t.name
    )

    if st.button("生成 HTML"):
        st.write("---")
        tabs = st.tabs([p.manage_number for p in selected_products])
        for i, product in enumerate(selected_products):
            with tabs[i]:
                st.subheader(product.manage_number)
                htmls = generate_html(product, pc_desc_tpl, pc_sales_tpl, mobile_tpl)
                for label, content in htmls.items():
                    with st.expander(label, expanded=False):
                        st.code(content, language="html")
                        # st.markdown(content, unsafe_allow_html=True)


if __name__ == "__main__":
    tools_page()
