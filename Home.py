import streamlit as st

st.set_page_config(
    page_title="後台管理系統",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚀 歡迎來到後台管理系統")
st.header("功能概覽")
st.write("---")

st.info("💡 **小撇步**：使用左側的側邊欄選單，可以快速切換不同功能。")

st.markdown("""
這個系統提供了多個強大的工具，協助你輕鬆管理商品和商店資訊。主要功能包括：

-   **Shops**：查詢、更新和管理所有商店的詳細資料。
-   **Products**：瀏覽、編輯和管理所有商品的庫存與資訊。
-   **Tools**：專為內部人員設計的特殊工具，用來自動化 HTML 頁面的生成和更新。
-   **Settings**：調整系統設定，並管理各種模板。

請點擊左側導覽列的連結，開始使用吧！
""")

st.write("---")
st.write("如果有任何問題或需要協助，請隨時聯繫開發團隊。")
st.write("感謝你的使用！")