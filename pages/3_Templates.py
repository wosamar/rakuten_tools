import streamlit as st
import pandas as pd
from pathlib import Path

from database.models import Template, TemplateType
from env_settings import EnvSettings
from handlers.database import DBHandler

env_settings = EnvSettings()


# ----------------- 資料查詢函式 -----------------
def _fetch_templates_data(db: DBHandler, template_name: str, template_type: str, all_types: list):
    query_conditions = {}
    if template_name:
        query_conditions['name'] = template_name
    if template_type and template_type != "全部":
        type_id = next((t.id for t in all_types if t.name == template_type), None)
        if type_id:
            query_conditions['template_type_id'] = type_id
    if query_conditions:
        return db.get_all(Template, **query_conditions)
    else:
        return db.get_all(Template)


# ----------------- 三個 Tab 函式 -----------------
def list_templates_tab(db: DBHandler, all_types: list):
    st.header("Template 列表 / 查詢")
    col1, col2 = st.columns(2)
    with col1:
        template_name = st.text_input("Template 名稱")
    with col2:
        selected_type = st.selectbox("類型", ["全部"] + [t.name for t in all_types])
    search_button = st.button("🔍 搜尋")

    if 'template_results' not in st.session_state or search_button:
        st.session_state.template_results = _fetch_templates_data(db, template_name, selected_type, all_types)

    results = st.session_state.template_results
    if results:
        df = pd.DataFrame([{
            'id': tpl.id,
            '名稱': tpl.name,
            '描述': tpl.description,
            '類型': tpl.template_type.name if tpl.template_type else None
        } for tpl in results])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("沒有找到符合條件的 Template。")


def add_template_tab(db: DBHandler, all_types: list):
    # TODO:名稱/檔名去重複
    st.header("新增 Template")
    with st.form("add_template_form"):
        name = st.text_input("名稱")
        description = st.text_input("描述")
        type_choice = st.selectbox("類型", [t.name for t in all_types])
        html_file = st.file_uploader("上傳 HTML 檔案", type=["html"])
        submitted = st.form_submit_button("新增")

        if submitted:
            type_id = next((t.id for t in all_types if t.name == type_choice), None)
            if not type_id:
                st.error("類型錯誤，無法新增")
            else:
                if html_file:
                    save_dir = env_settings.html_tmp_dir
                    save_dir.mkdir(parents=True, exist_ok=True)
                    file_path = save_dir / html_file.name
                    file_path.write_bytes(html_file.getbuffer())
                    path = html_file.name
                else:
                    path = None

                if not path:
                    st.error("請輸入路徑或上傳檔案")
                else:
                    new_template = Template(
                        name=name,
                        path=path,
                        description=description if description else None,
                        template_type_id=type_id,
                    )
                    db.add(new_template)
                    st.success("新增成功！請重新查詢。")


def preview_template_tab(db: DBHandler, all_types: list):
    st.header("Template 預覽")
    results = db.get_all(Template)
    if results:
        template_options = {tpl.name: tpl for tpl in results}
        selected_name = st.selectbox("選擇要預覽的 Template", [""] + list(template_options.keys()))
        if selected_name:
            tpl = template_options[selected_name]
            tpl_file = env_settings.html_tmp_dir / tpl.path
            with st.expander(f"{tpl.name} 原始碼", expanded=True):
                if tpl_file.exists():
                    html_content = tpl_file.read_text(encoding="utf-8")
                    st.code(html_content, language="html")
                else:
                    st.error("Template 檔案不存在")
    else:
        st.info("沒有可預覽的 Template。")


# ----------------- 主頁 -----------------
def templates_page():
    st.set_page_config(page_title="Templates", page_icon="📑", layout="wide")
    st.title("📑 Template 管理")
    st.write("---")

    db = DBHandler()
    all_types = db.get_all(TemplateType)

    tabs = st.tabs(["列表 / 查詢", "新增 Template", "預覽 Template"])
    with tabs[0]:
        list_templates_tab(db, all_types)
    with tabs[1]:
        add_template_tab(db, all_types)
    with tabs[2]:
        preview_template_tab(db, all_types)


if __name__ == "__main__":
    templates_page()
