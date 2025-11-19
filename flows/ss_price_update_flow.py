from typing import List
import math
from handlers.item_handler import ItemHandler


class SSPriceUpdateFlow:
    """
    A flow to update the standard and reference prices for all variants
    of specified items based on a given discount multiplier.
    """
    def __init__(self, auth_token: str, discount: float, logger=print):
        self.item_handler = ItemHandler(auth_token=auth_token)
        self.discount = discount
        self.logger = logger

    def run(self, item_ids: List[str]):
        if not (0 < self.discount <= 1):
            self.logger("Error: Discount must be between 0 and 1 (e.g., 0.8 for 80%).")
            return

        self.logger(f"Fetching {len(item_ids)} items...")
        items = self.item_handler.bulk_get_item(manage_numbers=item_ids)
        self.logger(f"Found {len(items)} items.")

        successful_items = []
        failed_items = {}

        for item in items:
            manage_number = item.get("manageNumber")
            if not manage_number:
                continue

            variants = item.get("variants", {})
            if not variants:
                self.logger(f"Skipping item {manage_number} as it has no variants.")
                continue

            self.logger(f"Processing item: {manage_number}")

            patch_payload = {"variants": {}}
            for variant_id, variant_details in variants.items():
                try:
                    reference_price_value_str = variant_details.get("referencePrice", {}).get("value")

                    if reference_price_value_str is not None:
                        original_price = int(reference_price_value_str)
                        self.logger(f"  - Variant {variant_id}: Using referencePrice value as original price: {original_price}")
                    else:
                        original_price_str = variant_details.get("standardPrice")

                        original_price = int(original_price_str)
                        self.logger(f"  - Variant {variant_id}: Using standardPrice as original price: {original_price}")
                    new_price = str(math.floor(original_price * self.discount))

                    self.logger(f"  - Variant {variant_id}: {original_price} -> {new_price}")

                    # Since we already checked that no variant has referencePrice, always add it now
                    variant_patch = {
                        "standardPrice": new_price,
                        "referencePrice": {
                            "displayType": "REFERENCE_PRICE",
                            "type": 1,
                            "value": str(original_price)
                        }
                    }

                    patch_payload["variants"][variant_id] = variant_patch
                except (ValueError, TypeError) as e:
                    self.logger(f"  - Could not process price for variant {variant_id}. Error: {e}. Skipping.")
                    continue

            if not patch_payload["variants"]:
                self.logger(f"No variants to update for item {manage_number}.")
                continue

            try:
                self.logger(f"Updating item {manage_number}...")
                self.item_handler.patch_item(manage_number, patch_payload)
                self.logger(f"Successfully updated item {manage_number}.")
                successful_items.append(manage_number)
            except Exception as e:
                error_message = f"Failed to update item {manage_number}. Error: {e}"
                self.logger(error_message)
                failed_items[manage_number] = str(e)

        self._log_summary(len(item_ids), successful_items, failed_items)

    def _log_summary(self, total: int, successful: list, failed: dict):
        self.logger("\n--- SS Price Update Flow Summary ---")
        self.logger(f"Total items attempted: {total}")
        self.logger(f"Successful: {len(successful)}")
        self.logger(f"Failed: {len(failed)}")

        if failed:
            self.logger("\nFailed items details:")
            for number, reason in failed.items():
                self.logger(f"  - {number}: {reason}")
        self.logger("--- Flow End ---")
