from typing import List, Dict, Any
import math
from handlers.item_handler import ItemHandler


class BasePriceFlow:
    """
    Base class for item price update flows.
    Handles fetching, processing, and updating items.
    """

    def __init__(self, auth_token: str, logger=print):
        self.item_handler = ItemHandler(auth_token=auth_token)
        self.logger = logger

    def run(self, item_ids: List[str]):
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

            patch_payload = self._process_item_variants(variants)

            if not patch_payload.get("variants"):
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

    def _process_item_variants(self, variants: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes all variants of an item and returns the patch payload.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError

    def _log_summary(self, total: int, successful: list, failed: dict):
        self.logger(f"\n--- {self.__class__.__name__} Summary ---")
        self.logger(f"Total items attempted: {total}")
        self.logger(f"Successful: {len(successful)}")
        self.logger(f"Failed: {len(failed)}")

        if failed:
            self.logger("\nFailed items details:")
            for number, reason in failed.items():
                self.logger(f"  - {number}: {reason}")
        self.logger("--- Flow End ---")


class PriceUpdater(BasePriceFlow):
    """
    Updates the standard and reference prices for all variants
    of specified items based on a given discount multiplier.
    """

    def __init__(self, auth_token: str, discount: float, logger=print):
        super().__init__(auth_token, logger)
        if not (0 < discount <= 1):
            raise ValueError("Discount must be between 0 and 1 (e.g., 0.8 for 80%).")
        self.discount = discount

    def _process_item_variants(self, variants: Dict[str, Any]) -> Dict[str, Any]:
        patch_payload = {"variants": {}}
        for variant_id, variant_details in variants.items():
            try:
                reference_price_value = variant_details.get("referencePrice", {}).get("value")
                original_price_str = reference_price_value or variant_details.get("standardPrice")

                if original_price_str is None:
                    self.logger(f"  - Variant {variant_id}: Could not determine original price. Skipping.")
                    continue

                original_price = int(original_price_str)
                new_price = str(math.floor(original_price * self.discount))

                self.logger(f"  - Variant {variant_id}: {original_price} -> {new_price}")

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
        return patch_payload


class PriceReversion(BasePriceFlow):
    """
    Reverts the price of item variants by setting the referencePrice
    as the new standardPrice and removing the referencePrice.
    """

    def _process_item_variants(self, variants: Dict[str, Any]) -> Dict[str, Any]:
        patch_payload = {"variants": {}}
        for variant_id, variant_details in variants.items():
            reference_price = variant_details.get("referencePrice", {}).get("value")

            if not reference_price:
                self.logger(f"  - Variant {variant_id}: No referencePrice found. Skipping.")
                continue

            try:
                original_price = int(reference_price)
                self.logger(f"  - Variant {variant_id}: Reverting to {original_price}")

                variant_patch = {
                    "standardPrice": str(original_price),
                    "referencePrice": None
                }
                patch_payload["variants"][variant_id] = variant_patch

            except (ValueError, TypeError) as e:
                self.logger(f"  - Could not process price for variant {variant_id}. Error: {e}. Skipping.")
                continue
        return patch_payload
