import streamlit as st
from flows.ss_campaign_update_flow import SSCampaignUpdateFlow
from env_settings import EnvSettings


def parse_input(input_string: str) -> list[str]:
    """
    解析使用者輸入的商品管理編號字串。
    """
    if not input_string:
        return []
    cleaned_string = input_string.replace('\n', ',')
    return [mn.strip() for mn in cleaned_string.split(',') if mn.strip()]


def run_flow(auth_token: str, manage_numbers: list[str]):
    """
    執行 SS Campaign 更新流程並將輸出顯示在 Streamlit 介面上。
    """
    log_area = st.empty()
    log_messages = []

    def streamlit_logger(message: str):
        """一個將訊息附加到列表並更新 Streamlit 元件的日誌記錄器。"""
        log_messages.append(message)
        log_area.code('\n'.join(log_messages))

    try:
        st.info(f"即將處理以下商品管理編號：{manage_numbers}")
        flow = SSCampaignUpdateFlow(auth_token, logger=streamlit_logger)

        with st.spinner("正在執行更新流程..."):
            flow.run(manage_numbers)

        st.success("SS Campaign 更新流程執行完畢！")

    except Exception as e:
        st.error(f"執行流程時發生未預期的錯誤：{e}")


def main():
    """
    Streamlit 頁面的主函數。
    """
    st.set_page_config(page_title="SS Campaign Updater", page_icon="🚀")

    st.title("🚀 SS Campaign Updater")
    st.write("此頁面用於執行超級特賣活動商品的更新流程。")

    env_settings = EnvSettings()
    auth_token = env_settings.auth_token

    manage_numbers_input = st.text_area(
        "請輸入商品管理編號 (Manage Numbers)，每個編號一行或以逗號分隔：",
        height=150,
        placeholder="例如：item1, item2, item3 或\nitem1\nitem2"
    )

    if st.button("開始執行 SS Campaign 更新流程"):
        manage_numbers = parse_input(manage_numbers_input)
        if manage_numbers:
            run_flow(auth_token, manage_numbers)
        else:
            st.warning("請輸入有效的商品管理編號。")


if __name__ == "__main__":
    main()
