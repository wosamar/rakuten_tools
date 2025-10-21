import streamlit as st
import json
import csv
import io

from flows.campaign_update_flow import CampaignUpdateFlow, CampaignConfig
from handlers.item_handler import ItemHandler
from models.item import ProductData
from env_settings import EnvSettings


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


def render_config_uploader():
    st.subheader("上傳設定檔")
    uploaded_config_file = st.file_uploader("上傳設定 JSON 檔案", type=["json"],
                                            help="上傳包含 config, point_campaigns, feature_campaign 的 JSON 檔案")

    if uploaded_config_file is not None:
        if st.button("載入設定檔"):
            try:
                uploaded_data = json.load(uploaded_config_file)
                if "config" in uploaded_data:
                    st.session_state[SessionStateKeys.POINT_TITLE] = uploaded_data["config"].get("point_title_format", "")
                    st.session_state[SessionStateKeys.POINT_HTML] = uploaded_data["config"].get("point_html_format", "")
                    st.session_state[SessionStateKeys.START_TIME_STR] = uploaded_data["config"].get("start_time", "")
                    st.session_state[SessionStateKeys.END_TIME_STR] = uploaded_data["config"].get("end_time", "")
                    st.session_state[SessionStateKeys.FEATURE_TITLE] = uploaded_data["config"].get("feature_title_format", "")
                    st.session_state[SessionStateKeys.FEATURE_HTML] = uploaded_data["config"].get("feature_html_format", "")
                    st.session_state[SessionStateKeys.NO_EVENT_HTML] = uploaded_data["config"].get("no_event_html_format", "")

                if "point_campaigns" in uploaded_data:
                    for i, campaign in enumerate(uploaded_data["point_campaigns"]):
                        key_suffix = str(i + 1)
                        st.session_state[SessionStateKeys.POINT_CAMPAIGN_POINTS_PREFIX.format(key_suffix)] = campaign.get("point_rate", 0)
                        st.session_state[SessionStateKeys.POINT_CAMPAIGN_IDS_PREFIX.format(key_suffix)] = "\n".join(campaign.get("items", []))

                if "feature_campaign" in uploaded_data:
                    st.session_state[SessionStateKeys.FEATURE_CAMPAIGN_CODE] = uploaded_data["feature_campaign"].get("campaign_code", "")
                    st.session_state[SessionStateKeys.FEATURE_IDS] = "\n".join(uploaded_data["feature_campaign"].get("items", []))

                st.success("設定檔已成功載入！")
            except json.JSONDecodeError:
                st.error("無效的 JSON 檔案格式。")
            except Exception as e:
                st.error(f"載入設定檔時發生錯誤: {e}")


def show_page():
    env_settings = EnvSettings()
    st.set_page_config(
        page_title="特輯與點數活動產生器",
        page_icon="✨",
        layout="wide"
    )
    st.title("特輯與點數活動產生器")

    # Initialize session state with default values if not already set
    if SessionStateKeys.POINT_TITLE not in st.session_state:
        st.session_state[SessionStateKeys.POINT_TITLE] = "10/24から{point_rate}倍ポイント {original_title}"
    if SessionStateKeys.POINT_HTML not in st.session_state:
        st.session_state[SessionStateKeys.POINT_HTML] = '<img src="https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_{point_rate}p_1080s.jpg"width="100%">{original_html}'
    if SessionStateKeys.START_TIME_STR not in st.session_state:
        st.session_state[SessionStateKeys.START_TIME_STR] = "2025-10-24T20:00:00+09:00"
    if SessionStateKeys.END_TIME_STR not in st.session_state:
        st.session_state[SessionStateKeys.END_TIME_STR] = "2025-10-27T09:59:59+09:00"
    if SessionStateKeys.FEATURE_TITLE not in st.session_state:
        st.session_state[SessionStateKeys.FEATURE_TITLE] = "{original_title}{campaign_code}"
    if SessionStateKeys.FEATURE_HTML not in st.session_state:
        st.session_state[SessionStateKeys.FEATURE_HTML] = '<a href="https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/"><img src="https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_kv_1280.jpg"width="100%"/>a>{original_html}'
    if SessionStateKeys.NO_EVENT_HTML not in st.session_state:
        st.session_state[SessionStateKeys.NO_EVENT_HTML] = '<a href="https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/"><img src="1024mr_kv_1280.jpg"width="100%"/>a>{original_html}'
    if SessionStateKeys.FEATURE_CAMPAIGN_CODE not in st.session_state:
        st.session_state[SessionStateKeys.FEATURE_CAMPAIGN_CODE] = ""
    if SessionStateKeys.FEATURE_IDS not in st.session_state:
        st.session_state[SessionStateKeys.FEATURE_IDS] = ""
    if "final_payloads" not in st.session_state:
        st.session_state["final_payloads"] = []

    # --- Upload Configuration Area ---
    render_config_uploader()

    # --- Template Input Area ---
    st.subheader("模板輸入")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 點數活動")
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

    with col2:
        st.markdown("#### 特輯活動")
        feature_title_format = st.text_input(
            "標題模板",
            key=SessionStateKeys.FEATURE_TITLE
        )
        feature_html_format = st.text_area(
            "HTML模板",
            key=SessionStateKeys.FEATURE_HTML,
            height=200
        )
        st.markdown("#### 無活動商品")
        no_event_html_format = st.text_area(
            "HTML模板",
            key=SessionStateKeys.NO_EVENT_HTML,
            height=200
        )

    # --- Item List Input Area ---
    st.subheader("商品清單輸入")
    st.write("---")
    st.write("點數活動商品清單")
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
            # Initialize session state for points if not present
            points_key = SessionStateKeys.POINT_CAMPAIGN_POINTS_PREFIX.format(config['key_suffix'])
            if points_key not in st.session_state:
                st.session_state[points_key] = config["default_points"]
            config["point_rate"] = st.number_input(
                "點數",
                key=points_key,
                min_value=1,
                step=5
            )
            # Initialize session state for items if not present
            ids_key = SessionStateKeys.POINT_CAMPAIGN_IDS_PREFIX.format(config['key_suffix'])
            if ids_key not in st.session_state:
                st.session_state[ids_key] = ""
            config["items"] = st.text_area("ID列表", key=ids_key, height=300)

    st.write("---")
    st.write("特輯商品清單")
    feature_campaign_code = st.text_input("活動代號", key=SessionStateKeys.FEATURE_CAMPAIGN_CODE)
    feature_item_list = st.text_area("ID列表", key=SessionStateKeys.FEATURE_IDS)

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

    if st.button("生成"):
        # --- Get All Products ---
        with st.spinner("正在從後台取得所有商品資料..."):
            item_handler = ItemHandler(env_settings.auth_token)
            all_items_raw = item_handler.search_item({}, page_size=10, max_page=1)
            all_products = [ProductData.from_api(item.get("item")) for item in all_items_raw]

        flow = CampaignUpdateFlow()
        final_payloads = flow.execute(
            all_products=all_products,
            config=campaign_config,
            point_campaigns=point_campaigns,
            feature_campaign=feature_campaign,
        )
        st.session_state["final_payloads"] = final_payloads

        # --- Display Results ---
        st.write("---")
        st.subheader("生成結果")
        st.json(json.dumps(final_payloads, indent=4, ensure_ascii=False), expanded=False)

    st.write("---")
    st.subheader("更新商品資訊")
    if st.button("執行商品更新"):
        if not st.session_state["final_payloads"]:
            st.warning("沒有可更新的商品資訊。請先點擊 '生成' 按鈕。")
            return

        item_handler = ItemHandler(env_settings.auth_token)
        updated_count = 0
        failed_updates = []

        for item_id, item_data in st.session_state["final_payloads"].items():
            try:
                # Create a ProductData object with only the manage_number and the generated payload
                # The to_patch_payload method will handle filtering None values
                product_to_update = ProductData(
                    manage_number=item_id,
                    **item_data["generated_payload"]
                )
                item_handler.patch_item(product_to_update)
                updated_count += 1
            except Exception as e:
                failed_updates.append(f"商品 {item_id} 更新失敗: {e}")

        if updated_count > 0:
            st.success(f"成功更新 {updated_count} 項商品！")
        if failed_updates:
            st.error("部分商品更新失敗:")
            for error_msg in failed_updates:
                st.write(error_msg)

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
