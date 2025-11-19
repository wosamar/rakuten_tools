import streamlit as st
from flows.ss_price_update_flow import SSPriceUpdateFlow
from env_settings import EnvSettings
from utils.streamlit_utils import parse_manage_numbers_input


def run_flow(auth_token: str, manage_numbers: list[str], discount: float):
    """
    Runs the SS Price Update flow and displays the output in the Streamlit interface.
    """
    log_area = st.empty()
    log_messages = []

    def streamlit_logger(message: str):
        """
        A logger that appends messages to a list and updates a Streamlit component.
        """
        log_messages.append(message)
        log_area.code('\n'.join(log_messages))

    try:
        st.info(f"正在處理以下商品管理編號：{manage_numbers}")
        flow = SSPriceUpdateFlow(auth_token, discount, logger=streamlit_logger)

        with st.spinner("正在執行更新流程..."):
            flow.run(manage_numbers)

        st.success("商品價格更新流程執行完畢！")

    except Exception as e:
        st.error(f"發生未預期的錯誤：{e}")


def main():
    """
    The main function for the Streamlit page.
    """
    st.set_page_config(page_title="SS Price Updater", page_icon="🏷️")

    st.title("🏷️ SS 商品價格更新器")
    st.write("此頁面用於根據折扣更新商品價格。")

    env_settings = EnvSettings()
    auth_token = env_settings.auth_token

    manage_numbers_input = st.text_area(
        "請輸入商品管理編號 (每行一個或以逗號分隔)：",
        height=150,
        placeholder="例如：item1, item2, item3 或\\nitem1\\nitem2"
    )

    discount_input = st.number_input(
        "請輸入折扣乘數 (例如，0.8 代表八折)：",
        min_value=0.01,
        max_value=1.0,
        value=0.8,
        step=0.01
    )

    if st.button("開始執行商品價格更新流程"):
        manage_numbers = parse_manage_numbers_input(manage_numbers_input)
        if not manage_numbers:
            st.warning("請輸入有效的商品管理編號。")
            return

        run_flow(auth_token, manage_numbers, discount_input)


if __name__ == "__main__":
    main()
