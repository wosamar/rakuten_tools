import streamlit as st

st.set_page_config(
    page_title="EC工具箱（Beta）",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚀 EC工具箱（Beta）")

st.warning("⚠️ **本系統為測試版本，僅供內部使用。** 功能仍在開發中，可能會存在不穩定或未完成之處。")

st.header("功能概覽")
st.write("---")

st.markdown("""
這個系統目前提供了一個強大的工具，協助你輕鬆將 Excel 商品文案轉換成 HTML 格式。

### 主要功能：
-   **Excel 轉 HTML 工具**：專為內部人員設計，用來自動化 HTML 頁面的生成和更新。
""")

st.info("💡 **小撇步**：使用左側的側邊欄選單，可以快速切換不同功能。")

st.markdown("""
### 聯絡支援
如果在測試過程中遇到任何問題或有功能建議，請隨時聯繫開發團隊，協助我們讓系統更臻完善。

""")
