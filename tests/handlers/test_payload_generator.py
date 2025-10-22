import json
from pathlib import Path
import pytest

from handlers.payload_generator import TitleGenerator, HtmlGenerator, PointCampaignGenerator
from models.item import ProductData, ProductDescription


# --- Test Case Loading ---

def load_test_cases(file_name):
    """Loads test cases from a JSON file."""
    test_case_path = Path(__file__).parent.parent.parent / "templates" / "test_case" / "payload_generator" / file_name
    with open(test_case_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    # Use the 'case' field as the test ID for better output
    return [pytest.param(case, id=case.get('case', f'case_{i}')) for i, case in enumerate(test_cases)]


# --- Test Functions ---

@pytest.mark.parametrize("test_case", load_test_cases("title_generator.json"))
def test_title_generator(test_case):
    """Tests the TitleGenerator class based on scenarios in title_generator.json."""
    # 1. Arrange
    input_data = test_case["input"]
    expected_output = test_case["output"]

    # Extract max_width from kwargs if present, otherwise use default
    max_width = input_data.get("max_width", 255)

    generator = TitleGenerator(title_format=input_data["title_format"], max_width=max_width)

    # 2. Act
    actual_output = generator.generate_title_payload(
        original_title_content=input_data["original_title_content"],
        **input_data["kwargs"]
    )

    # 3. Assert
    assert actual_output == expected_output


@pytest.mark.parametrize("test_case", load_test_cases("html_generator.json"))
def test_html_generator(test_case):
    """Tests the HtmlGenerator class based on scenarios in html_generator.json."""
    # 1. Arrange
    input_data = test_case["input"]
    expected_output = test_case["output"]

    # Convert dict to ProductData object
    product_data_dict = input_data["product_data"]
    if product_data_dict.get("product_description"):
        product_data_dict["product_description"] = ProductDescription(**product_data_dict["product_description"])
    product_data = ProductData(**product_data_dict)

    generator = HtmlGenerator(html_format=input_data["html_format"])

    # 2. Act
    actual_output = generator.generate_html_payload(
        product_data=product_data,
        **input_data["kwargs"]
    )

    # 3. Assert
    assert actual_output == expected_output


@pytest.mark.parametrize("test_case", load_test_cases("point_generator.json"))
def test_point_campaign_generator(test_case):
    """Tests the PointCampaignGenerator class based on scenarios in point_generator.json."""
    # 1. Arrange
    input_data = test_case["input"]
    expected_output = test_case["output"]

    generator = PointCampaignGenerator(
        start_time=input_data["start_time"],
        end_time=input_data["end_time"]
    )

    # 2. Act
    actual_output = generator.generate_point_campaign_payload(**input_data["kwargs"])

    # 3. Assert
    assert actual_output == expected_output
