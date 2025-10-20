from typing import Optional
from models.item import ProductData


class CampaignPayloadGenerator:
    """
    Generates a payload for updating product information based on campaign formats.
    """

    def __init__(
        self,
        title_format: Optional[str] = None,
        html_format: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ):
        """
        Initializes the payload generator with formatting templates and campaign times.

        Args:
            title_format: The format string for the product title.
                          Example: "10/24から{point_rate}倍ポイント {original_title}"
            html_format: The format string for the HTML content.
                         Example: "<img src='...'/>{original_html}"
            start_time: The start time for a point campaign (ISO 8601 format).
            end_time: The end time for a point campaign (ISO 8601 format).
        """
        self.title_format = title_format
        self.html_format = html_format
        self.start_time = start_time
        self.end_time = end_time

    def generate(self, product_data: ProductData, **kwargs) -> dict:
        """
        Generates the update payload for a given product.

        Args:
            product_data: The original product data object.
            **kwargs: Variables to be used in the format strings (e.g., point_rate).

        Returns:
            A dictionary representing the JSON payload for the update API.
        """
        payload = {}

        # Format Title
        if self.title_format:
            original_title = product_data.title or ""
            new_title = self.title_format.format(
                original_title=original_title, **kwargs
            )
            payload["title"] = new_title

        # Format HTML content
        if self.html_format:
            original_html = product_data.product_description or ""
            new_html = self.html_format.format(original_html=original_html, **kwargs)
            payload["productDescription"] = {"sp": new_html}
            payload["salesDescription"] = new_html

        # Create Point Campaign section
        if self.start_time and self.end_time and "point_rate" in kwargs:
            payload["pointCampaign"] = {
                "applicablePeriod": {"start": self.start_time, "end": self.end_time},
                "benefits": {"pointRate": str(kwargs["point_rate"])},
            }

        return payload
