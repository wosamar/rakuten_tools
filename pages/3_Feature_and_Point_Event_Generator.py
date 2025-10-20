import streamlit as st
import json
from datetime import datetime

from flows.campaign_update_flow import CampaignUpdateFlow, CampaignConfig
from handlers.item_handler import ItemHandler
from models.item import ProductData
from env_settings import EnvSettings


def show_page():
    st.set_page_config(
        page_title="特輯與點數活動產生器",
        page_icon="✨",
        layout="wide"
    )
    st.title("特輯與點數活動產生器")

    # --- Template Input Area ---
    st.subheader("模板輸入")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 點數活動")
        point_title_format = st.text_input(
            "標題模板",
            value="10/24から{point_rate}倍ポイント {original_title}",
            key="point_title"
        )
        point_html_format = st.text_area(
            "HTML模板",
            value='<img src="https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_{point_rate}p_1080s.jpg"width="100%">{original_html}',
            key="point_html",
            height=200
        )
        start_time_str = st.text_input("開始時間", "2025-10-24T20:00:00+09:00")
        end_time_str = st.text_input("結束時間", "2025-10-27T09:59:59+09:00")

    with col2:
        st.markdown("#### 特輯活動")
        feature_title_format = st.text_input(
            "標題模板",
            value="{original_title}{campaign_code}",
            key="feature_title"
        )
        feature_html_format = st.text_area(
            "HTML模板",
            value='<a href="https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/"><img src="https://image.rakuten.co.jp/giftoftw/cabinet/campagin/202510mr/1024mr_kv_1280.jpg"width="100%"/a>{original_html}',
            key="feature_html",
            height=200
        )
        st.markdown("#### 無活動商品")
        no_event_html_format = st.text_area(
            "HTML模板",
            value='<a href="https://www.rakuten.co.jp/giftoftw/contents/20251024_mr/"><img src="1024mr_kv_1280.jpg"width="100%"/a>{original_html}',
            key="no_event_html",
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
            config["point_rate"] = st.number_input(
                "點數",
                key=f"p{config['key_suffix']}_points",
                min_value=1,
                step=5,
                value=config["default_points"]
            )
            config["items"] = st.text_area("ID列表", key=f"p{config['key_suffix']}_ids", height=300)

    st.write("---")
    st.write("特輯商品清單")
    feature_campaign_code = st.text_input("活動代號")
    feature_item_list = st.text_area("ID列表", key="feature_ids")

    if st.button("生成"):
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

        # --- Get All Products ---
        with st.spinner("正在從後台取得所有商品資料..."):
            env_settings = EnvSettings()
            item_handler = ItemHandler(env_settings.auth_token)
            all_items_raw = item_handler.search_item({},page_size=5, max_page=1)
            all_products = [ProductData.from_api(item.get("item")) for item in all_items_raw]
            print(all_products)

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

        flow = CampaignUpdateFlow()
        final_payloads = flow.execute(
            all_products=all_products,
            config=campaign_config,
            point_campaigns=point_campaigns,
            feature_campaign=feature_campaign,
        )

        # --- Display Results ---
        st.write("---")
        st.subheader("生成結果")
        st.json(json.dumps(final_payloads, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    env_settings = EnvSettings() # Keep this commented out for demo purposes without API key
    show_page()