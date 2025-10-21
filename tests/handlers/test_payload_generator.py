import pytest
import re
from unittest.mock import Mock
from handlers.payload_generator import CampaignPayloadGenerator
from models.item import ProductData, ProductDescription, PointCampaign, ApplicablePeriod, Benefits


# Mock ProductData for testing
def create_mock_product_data(
        manage_number="test-001",
        title="Original Product Title",
        sp_description="<p>Original SP HTML</p>",
        pc_sales_description="<div>Original PC Sales HTML</div>",
        point_rate=None,
        start_time=None,
        end_time=None
):
    mock_product_description = ProductDescription(pc="", sp=sp_description)
    mock_point_campaign = None
    if point_rate is not None and start_time is not None and end_time is not None:
        mock_point_campaign = PointCampaign(
            applicablePeriod=ApplicablePeriod(start=start_time, end=end_time),
            benefits=Benefits(pointRate=point_rate)
        )

    return ProductData(
        manage_number=manage_number,
        title=title,
        product_description=mock_product_description,
        sales_description=pc_sales_description,
        point_campaign=mock_point_campaign
    )


class TestCampaignPayloadGenerator:

    # Test cases for _get_display_width
    @pytest.mark.parametrize(
        "text, expected_width",
        [
            ("abc", 3),
            ("你好", 4),
            ("Hello世界", 9),
            ("", 0),
            ("a中b文c", 7),  # 1+2+1+2+1
        ]
    )
    def test_get_display_width(self, text, expected_width):
        assert CampaignPayloadGenerator._get_display_width(text) == expected_width

    # Test cases for _generate_and_trim_title
    @pytest.mark.parametrize(
        "original_title, title_format, max_width, kwargs, expected_title",
        [
            # No trimming needed
            ("Short title", "Prefix {original_title} Suffix", 100, {}, "Prefix Short title Suffix"),
            ("Short title 【BRACKET】", "Prefix {original_title} Suffix", 100, {}, "Prefix Short title 【BRACKET】 Suffix"),
            # Trimming needed
            ("This is a very very very long title that needs to be trimmed", "{original_title}", 20, {},
             "This is a very very"),
            ("This is a very very very long title that needs to be trimmed", "Prefix {original_title}", 30, {},
             "Prefix This is a very very"),
            ("マグカップ ガラス グラス 350ml 耐熱 コップ ティーカップ ラウンドマグ 取っ手 透明 軽量 デザイン おしゃれ シンプル プレゼント ギフト お茶 カフェ 高品質 食器【TG】【台湾直送】【送料無料】【台湾エクセレンス】",
             "Campaign Title: {original_title}", 127, {},
             "Campaign Title: マグカップ ガラス グラス 350ml 耐熱 コップ ティーカップ ラウンドマグ 取っ手 透明 軽量 デザイン おしゃれ シンプル プレゼント ギフト お茶 カフェ 高品質 食器【TG】【台湾直送】【送料無料】【台湾エクセレンス】"),
            # Max width for CJK
            # Empty original title
            ("", "Prefix {original_title} Suffix", 50, {}, "Prefix  Suffix"),
            # Only brackets
            ("【ONLY BRACKETS】", "Prefix {original_title} Suffix", 50, {}, "Prefix 【ONLY BRACKETS】 Suffix"),
            # Kwargs in format
            ("Title", "{campaign_code} {original_title}", 50, {"campaign_code": "ABC"}, "ABC Title"),
            ("Long Title", "{campaign_code} {original_title}", 10, {"campaign_code": "ABC"}, "ABC Long"),
        ]
    )
    def test_generate_and_trim_title(self, original_title, title_format, max_width, kwargs, expected_title):
        generator = CampaignPayloadGenerator(title_format=title_format)
        trimmed_title = generator._generate_and_trim_title(
            original_title=original_title,
            max_width=max_width,
            **kwargs
        )
        assert trimmed_title == expected_title

    # Test cases for _apply_format_if_needed
    @pytest.mark.parametrize(
        "original_content, format_string, placeholder, formatter_func, kwargs, expected_output",
        [
            # Formatting applied (no existing prefix/suffix)
            ("Title", "Prefix {original_title} Suffix", "{original_title}", None, {}, "Prefix Title Suffix"),
            ("HTML", "<div>{original_html}</div>", "{original_html}", None, {}, "<div>HTML</div>"),
            # Formatting skipped (existing prefix/suffix)
            ("Prefix Title Suffix", "Prefix {original_title} Suffix", "{original_title}", None, {},
             "Prefix Title Suffix"),
            ("<div>HTML</div>", "<div>{original_html}</div>", "{original_html}", None, {}, "<div>HTML</div>"),
            # With formatter_func (for title trimming)
            ("Long Title Content", "Prefix {original_title}", "{original_title}",
             Mock(return_value="Prefix Long Title"), {}, "Prefix Long Title"),
            ("Prefix Long Title Content", "Prefix {original_title}", "{original_title}",
             Mock(return_value="Prefix Long Title Content"), {}, "Prefix Long Title Content"),  # Skipped
            # Kwargs affecting prefix/suffix
            ("CODE_ABC Title", "CODE_{campaign_code} {original_title}", "{original_title}", None,
             {"campaign_code": "ABC"}, "CODE_ABC Title"),  # Skipped
            ("Title", "CODE_{campaign_code} {original_title}", "{original_title}", None, {"campaign_code": "ABC"},
             "CODE_ABC Title"),  # Applied
        ]
    )
    def test_apply_format_if_needed(self, original_content, format_string, placeholder, formatter_func, kwargs,
                                    expected_output):
        # Initialize generator with the format_string if formatter_func is present, otherwise empty
        generator = CampaignPayloadGenerator(title_format=format_string if formatter_func else "", html_format="")

        result = generator._apply_format_if_needed(
            original_content=original_content,
            format_string=format_string,
            placeholder=placeholder,
            formatter_func=formatter_func,
            **kwargs
        )
        assert result == expected_output

    # Test cases for generate
    @pytest.mark.parametrize(
        "title_format, html_format, start_time, end_time, product_data_mock, kwargs, expected_payload",
        [
            # 前後皆重複更新
            ("New {original_title} 【Campaign】", None, None, None,
             create_mock_product_data(title="New Product Title 【Campaign】"),
             {},
             {"title": "New Product Title 【Campaign】"}
             ),
            # Only title update, no duplication
            ("New {original_title} Campaign", None, None, None,
             create_mock_product_data(title="Product Title"),
             {},
             {"title": "New Product Title Campaign"}),
            # Only HTML update, no duplication
            (None, "<p>New {original_html}</p>", None, None,
             create_mock_product_data(sp_description="<p>Old SP</p>"),
             {},
             {"productDescription": {"sp": "<p>New <p>Old SP</p></p>"},
              "salesDescription": "<p>New <div>Original PC Sales HTML</div></p>"}),
            # Point campaign update
            (None, None, "2025-01-01T00:00:00+09:00", "2025-01-07T23:59:59+09:00",
             create_mock_product_data(),
             {"point_rate": 10},
             {"pointCampaign": {
                 "applicablePeriod": {"start": "2025-01-01T00:00:00+09:00", "end": "2025-01-07T23:59:59+09:00"},
                 "benefits": {"pointRate": 10}}}),
            # Title and HTML update, with duplication check (should skip HTML)
            ("Title {original_title}", "<div>{original_html}</div>", None, None,
             create_mock_product_data(title="Original Title", sp_description="<div>Original SP HTML</div>"),
             {},
             {"title": "Title Original Title", "productDescription": {"sp": "<div>Original SP HTML</div>"},
              "salesDescription": "<div>Original PC Sales HTML</div>"}),
            # Title with kwargs, no duplication
            ("{code} {original_title}", None, None, None,
             create_mock_product_data(title="Product"),
             {"code": "XYZ"},
             {"title": "XYZ Product"}),
            # HTML with kwargs, no duplication
            (None, "<p>{code} {original_html}</p>", None, None,
             create_mock_product_data(sp_description="SP"),
             {"code": "XYZ"},
             {"productDescription": {"sp": "<p>XYZ SP</p>"},
              "salesDescription": "<p>XYZ <div>Original PC Sales HTML</div></p>"}),
            # All fields, no duplication
            ("T: {original_title}", "H: {original_html}", "2025-01-01T00:00:00+09:00", "2025-01-07T23:59:59+09:00",
             create_mock_product_data(title="Title", sp_description="SP", pc_sales_description="PC"),
             {"point_rate": 5},
             {
                 "title": "T: Title",
                 "productDescription": {"sp": "H: SP"},
                 "salesDescription": "H: PC",
                 "pointCampaign": {
                     "applicablePeriod": {"start": "2025-01-01T00:00:00+09:00", "end": "2025-01-07T23:59:59+09:00"},
                     "benefits": {"pointRate": 5}}
             }),
            # All fields, with duplication (should skip title and HTML)
            ("T: {original_title}", "H: {original_html}", "2025-01-01T00:00:00+09:00", "2025-01-07T23:59:59+09:00",
             create_mock_product_data(title="T: Original Title", sp_description="H: Original SP HTML",
                                      pc_sales_description="H: Original PC Sales HTML"),
             {"point_rate": 5},
             {
                 "title": "T: Original Title",
                 "productDescription": {"sp": "H: Original SP HTML"},
                 "salesDescription": "H: Original PC Sales HTML",
                 "pointCampaign": {
                     "applicablePeriod": {"start": "2025-01-01T00:00:00+09:00", "end": "2025-01-07T23:59:59+09:00"},
                     "benefits": {"pointRate": 5}}
             }),
        ]
    )
    def test_generate(self, title_format, html_format, start_time, end_time, product_data_mock, kwargs,
                      expected_payload):
        generator = CampaignPayloadGenerator(
            title_format=title_format,
            html_format=html_format,
            start_time=start_time,
            end_time=end_time,
        )
        payload = generator.generate(product_data_mock, **kwargs)
        assert payload == expected_payload
