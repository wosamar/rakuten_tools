import traceback
import requests
from handlers.item_handler import ItemHandler


class SSCampaignRevertFlow:
    """
    處理超級特賣 (Super Sale) 活動商品還原的流程。
    """

    def __init__(self, auth_token: str, logger=print):
        self.item_handler = ItemHandler(auth_token)
        self.logger = logger

    def run(self, manage_numbers: list[str]):
        """
        執行整個活動商品還原流程。
        """
        self.logger("--- SS Campaign Revert Flow Start ---")
        if not manage_numbers:
            self.logger("No items to process.")
            return

        successful_items = []
        failed_items = {}

        for manage_number in manage_numbers:
            self.logger(f"\nProcessing item for revert: {manage_number}")
            try:
                self._process_revert(manage_number)
                successful_items.append(manage_number)
                self.logger(f"  - Successfully reverted {manage_number}.")
            except requests.exceptions.HTTPError as e:
                error_message = f"Failed to revert {manage_number}. Reason: {e.response.status_code} {e.response.text}"
                self.logger(f"  - Error: {error_message}")
                failed_items[manage_number] = error_message
            except Exception as e:
                error_message = f"An unexpected error occurred while reverting {manage_number}. Reason: {e}"
                self.logger(f"  - Error: {error_message}")
                failed_items[manage_number] = error_message
                traceback.print_exc()

        self._log_summary(len(manage_numbers), successful_items, failed_items)

    def _process_revert(self, manage_number: str):
        """
        處理單一商品的還原流程。
        """
        # 1. 刪除 sscp 商品
        sscp_manage_number = f"{manage_number}_sscp"
        self._delete_sscp_item(sscp_manage_number)

        # 2. 還原原始商品狀態
        self._revert_original_item(manage_number)

    def _delete_sscp_item(self, manage_number: str):
        self.logger(f"  - Deleting campaign item: {manage_number}...")
        try:
            self.item_handler.delete_item(manage_number)
            self.logger(f"  - Successfully deleted {manage_number}.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.logger(f"  - Campaign item {manage_number} not found, skipping deletion.")
            else:
                raise

    def _revert_original_item(self, manage_number: str):
        self.logger(f"  - Reverting original item: {manage_number}...")
        payload = {
            "hideItem": False,
            "purchasablePeriod": None
        }
        self.item_handler.patch_item(manage_number, payload)
        self.logger(f"  - Unhidden and cleared purchasable period for {manage_number}.")

    def _log_summary(self, total: int, successful: list, failed: dict):
        self.logger("\n--- SS Campaign Revert Flow Summary ---")
        self.logger(f"Total items attempted: {total}")
        self.logger(f"Successful: {len(successful)}")
        self.logger(f"Failed: {len(failed)}")

        if failed:
            self.logger("\nFailed items details:")
            for number, reason in failed.items():
                self.logger(f"  - {number}: {reason}")
        self.logger("--- Flow End ---")
