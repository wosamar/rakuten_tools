from utils.campaign import parse_campaign_item_data

expected_output = {
    "manageNumber": "twe-acefly-01_sscp",
    "hideItem": "0",
    "purchasable_period": {
        "start": "2025-11-13T11:00:00",
        "end": "2025-12-02T19:59:59"
    },
    "articleNumber": {
        "value": "0"
    },
    "customField": "customValue"
}


def test_copy_campaign_items():
    item_data = {
        "manageNumber": "twe-acefly-01",
        "hideItem": "1",
        "articleNumber": {
            "value": "123"
        },
        "customField": "customValue"
    }

    res = parse_campaign_item_data(item_data)
    assert res == expected_output
