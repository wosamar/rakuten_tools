import traceback
from typing import Dict, Any

import requests

from handlers.inventory_handler import InventoryHandler
from handlers.item_handler import ItemHandler
from handlers.category_handler import CategoryHandler


class SSCampaignUpdateFlow:
    """
    處理超級特賣 (Super Sale) 活動商品更新的流程。
    """

    def __init__(self, auth_token: str, logger=print):
        self.item_handler = ItemHandler(auth_token)
        self.category_handler = CategoryHandler(auth_token)
        self.inventory_handler = InventoryHandler(auth_token)
        self.logger = logger
        # TODO:改為從外部設定 purchasablePeriod

    def run(self, manage_numbers: list[str]):
        """
        執行整個活動商品更新流程。
        """
        self.logger("--- SS Campaign Update Flow Start ---")
        if not manage_numbers:
            self.logger("No items to process.")
            return

        successful_items = []
        failed_items = {}

        for manage_number in manage_numbers:
            self.logger(f"\nProcessing item: {manage_number}")
            try:
                self._process_item(manage_number)
                successful_items.append(manage_number)
                self.logger(f"  - Successfully processed {manage_number}.")
            except requests.exceptions.HTTPError as e:
                error_message = f"Failed to process {manage_number}. Reason: {e.response.status_code} {e.response.text}"
                self.logger(f"  - Error: {error_message}")
                failed_items[manage_number] = error_message
            except Exception as e:
                error_message = f"An unexpected error occurred while processing {manage_number}. Reason: {e}"
                self.logger(f"  - Error: {error_message}")
                failed_items[manage_number] = error_message
                traceback.print_exc()

        self._log_summary(len(manage_numbers), successful_items, failed_items)

    def _process_item(self, manage_number: str):
        """
        處理單一商品的更新流程。
        """
        # 1. 取得商品和類別資訊
        item = self._get_item_data(manage_number)
        category_data = self._get_category_data(manage_number)

        # 2. 建立新的活動商品
        new_manage_number = f"{manage_number}_sscp"
        self._create_campaign_item(new_manage_number, item)

        # 3. 處理庫存
        self._handle_inventory(manage_number, new_manage_number)

        # 4. 設定新商品的類別
        self._update_category_mapping(new_manage_number, category_data)

        # 5. 更新原始商品狀態
        self._update_original_item_status(manage_number)

    def _get_item_data(self, manage_number: str) -> Dict[str, Any]:
        self.logger(f"  - Fetching detailed item data for {manage_number}...")
        return self.item_handler.get_item(manage_number)

    def _get_category_data(self, manage_number: str) -> Dict[str, Any]:
        self.logger(f"  - Getting category mapping for {manage_number}...")
        return self.category_handler.get_category_mapping(manage_number)

    def _create_campaign_item(self, new_manage_number: str, item_data: Dict[str, Any]):
        self.logger(f"  - Creating new campaign item: {new_manage_number}...")
        new_item = item_data.copy()
        new_item["hideItem"] = False
        new_item["purchasablePeriod"] = {
            "start": "2025-11-13T11:00:00+09:00",
            "end": "2025-12-02T19:59:59+09:00"
        }

        # 移除 API 不接受的欄位
        new_item.pop('manageNumber', None)
        new_item.pop('created', None)
        new_item.pop('updated', None)
        self.item_handler.upsert_item(new_manage_number, new_item)

    def _handle_inventory(self, original_manage_number: str, new_manage_number: str):
        self.logger(f"  - Fetching and setting inventory for variants...")
        variants_response = self.inventory_handler.get_variant_list(original_manage_number)
        variants = variants_response.get("variantList", [])

        if not variants:
            self.logger(f"    - No variants found for {original_manage_number}.")
            return

        self.logger(f"    - Found {len(variants)} variants.")
        inventory_query = [{"manageNumber": original_manage_number, "variantId": v} for v in variants]
        inventory_data = self.inventory_handler.bulk_get_inventory(inventory_query)
        inventories = inventory_data.get("inventories", [])

        if inventories:
            new_inventories = [
                {
                    "manageNumber": new_manage_number,
                    "variantId": inv["variantId"],
                    "mode": "ABSOLUTE",
                    "quantity": inv.get("quantity", 0)
                }
                for inv in inventories
            ]
            self.inventory_handler.bulk_upsert(new_inventories)
            self.logger(f"    - Successfully set inventory for {len(new_inventories)} variants of {new_manage_number}.")

    def _update_category_mapping(self, new_manage_number: str, category_data: Dict[str, Any]):
        self.logger(f"  - Setting category for {new_manage_number}...")
        self.category_handler.update_category_mapping(
            new_manage_number,
            category_data["categoryIds"],
            category_data.get("mainPluralCategoryId")
        )

    def _update_original_item_status(self, manage_number: str):
        self.logger(f"  - Updating original item: {manage_number}...")
        payload = {
            "hideItem": True,
            "purchasablePeriod": {
                "start": "2025-12-03T20:00:00+09:00",
                "end": "2025-12-11T01:59:59+09:00"
            }
        }
        self.item_handler.patch_item(manage_number, payload)

    def _log_summary(self, total: int, successful: list, failed: dict):
        self.logger("\n--- SS Campaign Update Flow Summary ---")
        self.logger(f"Total items attempted: {total}")
        self.logger(f"Successful: {len(successful)}")
        self.logger(f"Failed: {len(failed)}")

        if failed:
            self.logger("\nFailed items details:")
            for number, reason in failed.items():
                self.logger(f"  - {number}: {reason}")
        self.logger("--- Flow End ---")
