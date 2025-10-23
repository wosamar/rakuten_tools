import json
from pathlib import Path
import pytest
from flows.campaign_update_flow import CampaignUpdateFlow, CampaignConfig
from models.item import ProductData, ProductDescription


def load_test_case():
    test_case_path = Path(__file__).parent.parent.parent / "templates" / "test_case" / "campaign_update_flow.json"
    with open(test_case_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def campaign_data():
    return load_test_case()


def test_campaign_update_flow(campaign_data):
    # 1. Arrange
    input_data = campaign_data["input"]
    expected_output = campaign_data["out_put"]

    all_products = [ProductData(**p) for p in input_data["all_products"]]
    config = CampaignConfig(**input_data["config"])
    point_campaigns = input_data["point_campaigns"]
    feature_campaigns = input_data["feature_campaigns"]

    flow = CampaignUpdateFlow()

    # 2. Act
    actual_output = flow.execute(
        all_products=all_products,
        config=config,
        point_campaigns=point_campaigns,
        feature_campaigns=feature_campaigns,
    )

    # 3. Assert
    assert actual_output == expected_output
