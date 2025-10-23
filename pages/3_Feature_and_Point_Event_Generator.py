from datetime import date

import streamlit as st
import json

from urllib3.exceptions import MaxRetryError

from flows.campaign_update_flow import CampaignUpdateFlow, CampaignConfig
from handlers.item_handler import ItemHandler
from models.item import ProductData
from env_settings import EnvSettings

env_settings = EnvSettings()


class SessionStateKeys:
    # Config
    POINT_TITLE = "point_title"
    POINT_HTML = "point_html"
    START_TIME_STR = "start_time_str"
    END_TIME_STR = "end_time_str"
    FEATURE_TITLE = "feature_title"
    FEATURE_HTML = "feature_html"
    NO_EVENT_HTML = "no_event_html"

    # Point Campaigns (dynamic keys)
    POINT_CAMPAIGN_POINTS_PREFIX = "p{}_points"
    POINT_CAMPAIGN_IDS_PREFIX = "p{}_ids"

    # Feature Campaign
    FEATURE_CAMPAIGN_CODE = "feature_campaign_code"
    FEATURE_IDS = "feature_ids"


def init_session_state():
    if SessionStateKeys.POINT_TITLE not in st.session_state:
        st.session_state[SessionStateKeys.POINT_TITLE] = "10/24から{point_rate}倍ポイント {original_title}"
    if SessionStateKeys.POINT_HTML not in st.session_state:
        st.session_state[
            SessionStateKeys.POINT_HTML] = '<img src="https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_{point_rate}p_1080s.jpg"width="100%">{original_html}'
    if SessionStateKeys.START_TIME_STR not in st.session_state:
        st.session_state[SessionStateKeys.START_TIME_STR] = "2025-10-24T20:00:00+09:00"
    if SessionStateKeys.END_TIME_STR not in st.session_state:
        st.session_state[SessionStateKeys.END_TIME_STR] = "2025-10-27T09:59:59+09:00"
    if SessionStateKeys.FEATURE_TITLE not in st.session_state:
        st.session_state[SessionStateKeys.FEATURE_TITLE] = "{original_title}{campaign_code}"
    if SessionStateKeys.FEATURE_HTML not in st.session_state:
        st.session_state[
            SessionStateKeys.FEATURE_HTML] = '<a href="https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/"><img src="https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_kv_1280.jpg"width="100%"/></a>{original_html}'
    if SessionStateKeys.NO_EVENT_HTML not in st.session_state:
        st.session_state[
            SessionStateKeys.NO_EVENT_HTML] = '<a href="https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/"><img src="https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_kv_1280.jpg"width="100%"/></a><a href="https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/"><img src="https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_kv_1280.jpg"width="100%"/></a>{original_html}'
    if SessionStateKeys.FEATURE_CAMPAIGN_CODE not in st.session_state:
        st.session_state[SessionStateKeys.FEATURE_CAMPAIGN_CODE] = ""
    if SessionStateKeys.FEATURE_IDS not in st.session_state:
        st.session_state[SessionStateKeys.FEATURE_IDS] = ""
    if "final_payloads" not in st.session_state:
        st.session_state["final_payloads"] = []


def render_config_uploader():
    st.subheader("上傳設定檔")
    uploaded_config_file = st.file_uploader("上傳設定 JSON 檔案", type=["json"],
                                            help="上傳包含 config, point_campaigns, feature_campaign 的 JSON 檔案")

    if st.button("載入設定檔"):
        if uploaded_config_file is None:
            st.warning("請先上傳設定檔")
        else:
            try:
                uploaded_data = json.load(uploaded_config_file)
                if "config" in uploaded_data:
                    st.session_state[SessionStateKeys.POINT_TITLE] = uploaded_data["config"].get("point_title_format",
                                                                                                 "")
                    st.session_state[SessionStateKeys.POINT_HTML] = uploaded_data["config"].get("point_html_format", "")
                    st.session_state[SessionStateKeys.START_TIME_STR] = uploaded_data["config"].get("start_time", "")
                    st.session_state[SessionStateKeys.END_TIME_STR] = uploaded_data["config"].get("end_time", "")
                    st.session_state[SessionStateKeys.FEATURE_TITLE] = uploaded_data["config"].get(
                        "feature_title_format", "")
                    st.session_state[SessionStateKeys.FEATURE_HTML] = uploaded_data["config"].get("feature_html_format",
                                                                                                  "")
                    st.session_state[SessionStateKeys.NO_EVENT_HTML] = uploaded_data["config"].get(
                        "no_event_html_format", "")

                if "point_campaigns" in uploaded_data:
                    for i, campaign in enumerate(uploaded_data["point_campaigns"]):
                        key_suffix = str(i + 1)
                        st.session_state[
                            SessionStateKeys.POINT_CAMPAIGN_POINTS_PREFIX.format(key_suffix)] = campaign.get(
                            "point_rate", 0)
                        st.session_state[SessionStateKeys.POINT_CAMPAIGN_IDS_PREFIX.format(key_suffix)] = "\n".join(
                            campaign.get("items", []))

                if "feature_campaign" in uploaded_data:
                    st.session_state[SessionStateKeys.FEATURE_CAMPAIGN_CODE] = uploaded_data["feature_campaign"].get(
                        "campaign_code", "")
                    st.session_state[SessionStateKeys.FEATURE_IDS] = "\n".join(
                        uploaded_data["feature_campaign"].get("items", []))

                st.success("設定檔已成功載入！")
            except json.JSONDecodeError:
                st.error("無效的 JSON 檔案格式。")
            except Exception as e:
                st.error(f"載入設定檔時發生錯誤: {e}")


def generate_payloads(campaign_config, point_campaigns, feature_campaign, target_item_ids: list[str] | None = None):
    # --- Get All Products ---
    with st.spinner("正在從後台取得所有商品資料..."):
        try:
            item_handler = ItemHandler(env_settings.auth_token)
            if target_item_ids:
                all_items_raw = item_handler.bulk_get_item(target_item_ids)
                all_products = [ProductData.from_api(item) for item in all_items_raw]
                st.info(f"共取得 {len(all_products)} 筆指定商品")
            else:
                all_items_raw = item_handler.search_item({"updatedFrom": f"{date.today().year}-01-01"}, page_size=100,
                                                         max_page=20)
                all_products = [ProductData.from_api(item.get("item")) for item in all_items_raw]
                st.info(f"共取得 {len(all_products)} 筆商品")
        except MaxRetryError:
            st.error("連線超時，請再試一次")
            return

    with st.spinner("正在生成Payload..."):
        flow = CampaignUpdateFlow()
        final_payloads = flow.execute(
            all_products=all_products,
            config=campaign_config,
            point_campaigns=point_campaigns,
            feature_campaign=feature_campaign,
        )
    st.session_state["final_payloads"] = final_payloads


def render_results():
    if "final_payloads" in st.session_state and st.session_state["final_payloads"]:
        st.write("---")
        st.subheader("生成結果")
        payload_items = list(st.session_state["final_payloads"].items())
        total_items = len(payload_items)
        items_per_page = 20
        total_pages = (total_items + items_per_page - 1) // items_per_page

        if total_pages > 0:
            # Initialize page_number in session state if it doesn't exist
            if "page_number" not in st.session_state:
                st.session_state["page_number"] = 1

            # Ensure page_number is within valid range
            if st.session_state["page_number"] > total_pages:
                st.session_state["page_number"] = total_pages

            page_number = st.number_input(
                '頁數',
                min_value=1,
                max_value=total_pages,
                key="page_number",
                step=1
            )

            start_index = (page_number - 1) * items_per_page
            end_index = min(start_index + items_per_page, total_items)
            st.text(f"總筆數: {total_items} / 總頁數: {total_pages} / 目前顯示第 {start_index + 1}-{end_index} 筆")

            paginated_payloads = dict(payload_items[start_index:end_index])

            st.json(json.dumps(paginated_payloads, indent=4, ensure_ascii=False), expanded=False)


def execute_item_update():
    if not st.session_state["final_payloads"]:
        st.warning("沒有可更新的商品資訊。請先點擊 '生成' 按鈕。")
        return

    item_handler = ItemHandler(env_settings.auth_token)
    updated_count = 0
    failed_updates = []

    total_items = len(st.session_state["final_payloads"])
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, (item_id, item_data) in enumerate(st.session_state["final_payloads"].items()):
        try:
            # Create a ProductData object with only the manage_number and the generated payload
            # The to_patch_payload method will handle filtering None values
            status_text.text(f"正在更新商品: {item_id} ({i + 1}/{total_items})")
            item_handler.patch_item(item_id, item_data)
            updated_count += 1
        except Exception as e:
            failed_updates.append(f"商品 {item_id} 更新失敗: {e}")

        progress_bar.progress((i + 1) / total_items)

    status_text.text("更新完成！")

    if updated_count > 0:
        st.success(f"成功更新 {updated_count} 項商品！")
    if failed_updates:
        st.error("部分商品更新失敗:")
        for error_msg in failed_updates:
            st.write(error_msg)


def show_page():
    st.set_page_config(
        page_title="特輯與點數活動產生器",
        page_icon="✨",
        layout="wide"
    )
    st.title("特輯與點數活動產生器")

    # Initialize session state with default values if not already set
    init_session_state()

    # --- Upload Configuration Area ---
    render_config_uploader()

    # --- Template Input Area ---
    st.subheader("模板輸入")

    tab_point, tab_feature, tab_no_event = st.tabs(["點數活動", "特輯活動", "無活動"])

    with tab_point:
        st.markdown("#### 點數活動設定")
        point_title_format = st.text_input(
            "標題模板",
            key=SessionStateKeys.POINT_TITLE
        )
        point_html_format = st.text_area(
            "HTML模板",
            key=SessionStateKeys.POINT_HTML,
            height=200
        )
        start_time_str = st.text_input("開始時間", key=SessionStateKeys.START_TIME_STR)
        end_time_str = st.text_input("結束時間", key=SessionStateKeys.END_TIME_STR)

        st.write("---")
        st.markdown("#### 點數活動商品清單")
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        point_campaigns_inputs = [
            {"col": p_col1, "key_suffix": "1", "default_points": 5},
            {"col": p_col2, "key_suffix": "2", "default_points": 10},
            {"col": p_col3, "key_suffix": "3", "default_points": 15},
            {"col": p_col4, "key_suffix": "4", "default_points": 20},
        ]

        for config in point_campaigns_inputs:
            with config["col"]:
                st.markdown(f"##### 點數活動商品清單 {config['key_suffix']}")
                points_key = SessionStateKeys.POINT_CAMPAIGN_POINTS_PREFIX.format(config['key_suffix'])
                if points_key not in st.session_state:
                    st.session_state[points_key] = config["default_points"]
                config["point_rate"] = st.number_input(
                    "點數",
                    key=points_key,
                    min_value=1,
                    step=5
                )
                ids_key = SessionStateKeys.POINT_CAMPAIGN_IDS_PREFIX.format(config['key_suffix'])
                if ids_key not in st.session_state:
                    st.session_state[ids_key] = ""
                config["items"] = st.text_area("ID列表", key=ids_key, height=300)

    with tab_feature:
        st.markdown("#### 特輯活動設定")
        feature_title_format = st.text_input(
            "標題模板",
            key=SessionStateKeys.FEATURE_TITLE
        )
        feature_html_format = st.text_area(
            "HTML模板",
            key=SessionStateKeys.FEATURE_HTML,
            height=200
        )
        st.write("---")
        st.markdown("#### 特輯商品清單")
        feature_campaign_code = st.text_input("活動代號", key=SessionStateKeys.FEATURE_CAMPAIGN_CODE)
        feature_item_list = st.text_area("ID列表", key=SessionStateKeys.FEATURE_IDS)

    with tab_no_event:
        st.markdown("#### 無活動商品設定")
        no_event_html_format = st.text_area(
            "HTML模板",
            key=SessionStateKeys.NO_EVENT_HTML,
            height=200
        )

    # --- Collect Point Campaigns ---
    point_campaigns = []
    for config in point_campaigns_inputs:
        item_ids = {line.strip() for line in config["items"].split('\n') if line.strip()}
        if item_ids:
            point_campaigns.append({
                "point_rate": config["point_rate"],
                "items": list(item_ids)
            })

    # --- Collect Feature Campaign ---
    feature_item_ids = {line.strip() for line in feature_item_list.split('\n') if line.strip()}
    feature_campaign = {
        "campaign_code": feature_campaign_code,
        "items": list(feature_item_ids)
    }

    # --- Setup and Execute Campaign Flow ---
    campaign_config = CampaignConfig(
        point_title_format=point_title_format,
        point_html_format=point_html_format,
        start_time=start_time_str,
        end_time=end_time_str,
        feature_title_format=feature_title_format,
        feature_html_format=feature_html_format,
        no_event_html_format=no_event_html_format,
    )

    # --- Generate Payloads ---
    st.write("---")
    st.subheader("指定商品")
    target_item_ids_str = st.text_area("指定商品 manage_number (一行一個)，如果為空則處理所有商品")

    if st.button("生成"):
        st.session_state["final_payloads"] = []  # Clear previous results
        st.session_state["page_number"] = 1  # Reset page number
        target_item_ids = list(set(line.strip() for line in target_item_ids_str.split('\n') if line.strip()))
        generate_payloads(campaign_config, point_campaigns, feature_campaign, target_item_ids)

    # --- Display Results ---
    render_results()

    st.write("---")
    st.subheader("更新商品資訊")
    st.info("更新前請先至後台下載 csv 備份")

    if st.button("執行商品更新"):
        execute_item_update()

    # --- Download Combined JSON ---
    st.subheader("下載設定檔")
    combined_data = {
        "config": campaign_config.model_dump(),  # Assuming CampaignConfig has a .model_dump() method
        "point_campaigns": point_campaigns,
        "feature_campaign": feature_campaign,
    }
    json_download_str = json.dumps(combined_data, indent=4, ensure_ascii=False)
    st.download_button(
        label="下載設定 JSON",
        data=json_download_str,
        file_name="campaign_settings.json",
        mime="application/json"
    )


if __name__ == '__main__':
    show_page()
