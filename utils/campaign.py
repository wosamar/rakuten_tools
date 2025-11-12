from env_settings import EnvSettings
from handlers.item_handler import ItemHandler

env_settings = EnvSettings()


def copy_campaign_items(item_handler, manage_numbers):
    items = item_handler.bulk_get_item(manage_numbers)
    for item in items:
        new_item = parse_campaign_item_data(item)
        manage_number = new_item.pop("manage_number")

        item_handler.upsert_item(manage_number, new_item)
        break


def parse_campaign_item_data(item_data):
    new_item = item_data.copy()
    new_item["manageNumber"] = f"{item_data['manageNumber']}_sscp"
    new_item["hideItem"] = "0"
    new_item["purchasable_period"] = {
        "start": "2025-11-13T11:00:00",
        "end": "2025-12-02T19:59:59"
    }
    new_item["articleNumber"] = {
        "value": "0"
    }
    return new_item


if __name__ == '__main__':
    item_handler = ItemHandler(env_settings.auth_token)
    manage_numbers = [
        "twe-acefly-01", "twe-acefly-02", "twe-acefly-03", "twe-acefly-04", "twe-acefly-05", "twe-acefly-06",
        "twe-acera-01", "twe-acera-02", "twe-acera-03", "twe-acera-04", "twe-acera-05", "twe-acera-06", "twe-acera-07",
        "twe-acera-08", "twe-acera-09", "twe-acera-10", "twe-aifa-01", "twe-aifa-02", "twe-aifa-03", "twe-aifa-04",
        "twe-aw-01", "twe-aw-02", "twe-aw-03", "twe-aw-04", "twe-aw-05", "twe-aw-06", "twe-aw-07", "twe-aw-08",
        "twe-aw-09", "twe-dc-01", "twe-feca-02", "twe-feca-08", "twe-feca-14", "twe-feca-22", "twe-mbranfiltra-01",
        "twe-mbranfiltra-03", "twe-mosa-01", "twe-mosa-02", "twe-piao-i-001", "twe-piao-i-002", "twe-piao-i-003",
        "twe-piao-i-004", "twe-piao-i-005", "twe-piao-i-006", "twe-piao-i-007", "twe-piao-i-008", "twe-piao-i-009",
        "twe-piao-i-010", "twe-piao-i-011", "twe-piao-i-012", "twe-piao-i-013", "twe-playme-01", "twe-playme-02",
        "twe-playme-03", "twe-saeko-01", "twe-saeko-03", "twe-saeko-06", "twe-saeko-09", "twe-shinebeam-01",
        "twe-shinebeam-02", "twe-shinebeam-03", "twe-shinebeam-04", "twe-shinebeam-05", "twe-shinebeam-06",
        "twe-shinebeam-07", "twe-shinebeam-08", "twe-shinebeam-09", "twe-shinebeam-10", "twe-shrd-01", "twe-shrd-02",
        "twe-shrd-03", "twe-smartmatrix-01", "twe-ultracker-01", "twe-taku-01", "twe-taku-02", "twe-taku-03",
        "twe-taku-04", "twe-taku-05", "twe-taku-06", "twe-taku-07", "twe-taku-08", "twe-taku-09", "tra-ogift-01",
        "tra-ogift-02", "tra-letsdrink-05", "tra-letsdrink-06", "tra-letsdrink-01", "tra-ambassador-03", "tra-hyuga-01",
        "tra-hyuga-04", "tra-hyuga-06", "tra-wanwen-01", "tra-wanwen-03", "tra-wanwen-04", "tra-lotboard-01",
        "tra-lotboard-02", "tra-lotboard-03", "tra-lotboard-04", "tra-lotboard-05", "tra-gemcrown-01",
        "tra-gemcrown-02", "tra-gemcrown-03", "tra-gemcrown-04", "tra-gemcrown-05", "tra-goeco-01", "tra-goeco-02",
        "tra-4u4u-03", "tra-washi-01", "tra-washi-04", "tra-washi-02", "tra-washi-03", "tra-aquahex-01",
        "tra-echobuckle-01", "tra-echobuckle-02", "tra-echobuckle-03", "tra-echobuckle-04", "tra-echobuckle-05",
        "tra-tne-01", "tra-tne-02", "tra-tne-03", "tra-tne-04", "tra-tne-05", "tra-alody-03", "tra-azureland-02",
        "tra-azureland-03", "tra-azureland-04", "tra-azureland-05", "tra-bull-02", "tra-bull-04", "tra-bull-05",
        "tra-bull-06", "tra-healthbody-01", "tra-healthbody-06", "tra-healthbody-07", "tra-healthbody-04",
        "tra-healthbody-05", "tra-janda-01", "tra-janda-06", "tra-fonming-02", "tra-fonming-04", "tra-fonming-05",
        "tra-fonming-01", "tra-fonming-03", "tra-nexcom-01", "tra-nexcom-02", "tra-sonnac-01", "tra-sonnac-02",
        "tra-sonnac-03", "tra-sonnac-04", "tra-sonnac-05", "tra-caspard-01", "tra-caspard-02", "tra-caspard-03",
        "tra-caspard-04", "tra-3part-01", "tra-hiq-01", "tra-hiq-02", "tra-hiq-06", "tra-hiq-05", "tra-cura-01",
        "tra-lifenergy-01", "tra-lifenergy-04", "tra-lifenergy-05", "tra-lifenergy-06", "tra-lifenergy-08",
        "tra-tongwang-06", "tra-hic-01", "tra-gh-01", "tra-gh-02", "tra-gh-04", "tra-gh-05", "tra-gh-03",
        "tra-chauwan-01", "tra-unemac-01", "tra-unemac-02", "tra-unemac-03", "tra-unemac-04", "tra-unemac-05",
        "twe-jinsui-01", "twe-jinsui-02", "twe-jinsui-03", "twe-jinsui-04", "twe-jinsui-05", "twe-jinsui-07",
        "twe-jinsui-08", "twe-jinsui-09", "twe-jinsui-10"
    ]
    copy_campaign_items(item_handler, manage_numbers=manage_numbers)
