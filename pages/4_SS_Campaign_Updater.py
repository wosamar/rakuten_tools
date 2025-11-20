import streamlit as st
from flows.ss_campaign_update_flow import SSCampaignUpdateFlow
from flows.ss_campaign_revert_flow import SSCampaignRevertFlow
from env_settings import EnvSettings
from datetime import datetime, timedelta, timezone
from utils.streamlit_utils import parse_manage_numbers_input

JST = timezone(timedelta(hours=9))


def run_flow(auth_token: str, manage_numbers: list[str], mode: str, campaign_start: str = None, campaign_end: str = None):
    """
    執行 SS Campaign 更新或還原流程，並將輸出顯示在 Streamlit 介面上。
    """
    log_area = st.empty()
    log_messages = []

    def streamlit_logger(message: str):
        """
        一個將訊息附加到列表並更新 Streamlit 元件的日誌記錄器。
        """
        log_messages.append(message)
        log_area.code('\n'.join(log_messages))

    try:
        st.info(f"即將處理以下商品管理編號：{manage_numbers}")

        if mode == "Create Campaign Items":
            flow = SSCampaignUpdateFlow(auth_token, campaign_start, campaign_end, logger=streamlit_logger)
        else:  # Revert Campaign Items
            flow = SSCampaignRevertFlow(auth_token, logger=streamlit_logger)

        with st.spinner("正在執行流程..."):
            flow.run(manage_numbers)

        st.success(f"SS Campaign {mode} 流程執行完畢！")

    except Exception as e:
        st.error(f"執行流程時發生未預期的錯誤：{e}")


def main():
    """
    Streamlit 頁面的主函數。
    """
    st.set_page_config(page_title="SS Campaign Manager", page_icon="🚀")

    st.title("🚀 SS Campaign Manager")
    st.write("此頁面用於建立或還原 Super Sale 活動商品。（時區為GMT+9）")

    env_settings = EnvSettings()
    auth_token = env_settings.auth_token

    mode = st.radio(
        "請選擇操作模式：",
        ("Create Campaign Items", "Revert Campaign Items"),
        horizontal=True
    )

    manage_numbers_input = st.text_area(
        "請輸入商品管理編號 (Manage Numbers)，每個編號一行或以逗號分隔：",
        height=150,
        placeholder="例如：item1, item2, item3 或\nitem1\nitem2"
    )

    campaign_start, campaign_end = None, None
    if mode == "Create Campaign Items":
        st.subheader("活動時間設定")
        campaign_start_date = st.date_input("活動開始日期", value=datetime.now(JST).date() + timedelta(days=20))
        campaign_start_time = st.time_input("活動開始時間", value=datetime.strptime("20:00", "%H:%M").time())

        default_campaign_end_date = datetime.now(JST).date() + timedelta(days=29)
        campaign_end_date = st.date_input("活動結束日期", value=default_campaign_end_date)
        campaign_end_time = st.time_input("活動結束時間", value=datetime.strptime("01:59", "%H:%M").time())

        campaign_start_dt = datetime.combine(campaign_start_date, campaign_start_time)
        campaign_start = campaign_start_dt.replace(tzinfo=JST).isoformat(timespec='seconds')

        campaign_end_dt = datetime.combine(campaign_end_date, campaign_end_time)
        campaign_end = campaign_end_dt.replace(tzinfo=JST).isoformat(timespec='seconds')

    if st.button("開始執行流程"):
        manage_numbers = parse_manage_numbers_input(manage_numbers_input)
        if not manage_numbers:
            st.warning("請輸入有效的商品管理編號。")
            return

        run_flow(auth_token, manage_numbers, mode, campaign_start=campaign_start, campaign_end=campaign_end)


if __name__ == "__main__":
    main()
