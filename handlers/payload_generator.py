import unicodedata
import re
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
        self.title_format = title_format
        self.html_format = html_format
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def _get_display_width(text: str) -> int:
        width = 0
        for char in text:
            if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
                width += 2
            else:
                width += 1
        return width

    def _generate_and_trim_title(
        self, original_title: str, max_width: int = 255, **kwargs
    ) -> str:
        """
        Generates a title by first trimming the original_title to fit within
        the campaign text frame, then combines them.
        max_width = 半形 255 = 全形 127
        """
        if not self.title_format:
            return original_title

        # 1. Extract bracketed text
        bracketed_texts = re.findall(r'【.*?】', original_title)
        
        # Create a version of the original title without bracketed texts for width calculation and trimming
        original_title_without_brackets_for_trimming = original_title
        for bracketed_text in bracketed_texts:
            original_title_without_brackets_for_trimming = original_title_without_brackets_for_trimming.replace(bracketed_text, '')

        # 2. Calculate the width of the "frame" (the format string without original_title)
        #    by substituting all other placeholders.
        temp_title_for_frame = self.title_format.replace("{original_title}", "")
        frame_text = temp_title_for_frame.format(original_title="", **kwargs)
        frame_width = self._get_display_width(frame_text)

        # 3. Determine the max allowed width for the original title (excluding bracketed text)
        bracketed_width = sum(self._get_display_width(text) for text in bracketed_texts)
        allowed_title_width = max_width - frame_width - bracketed_width

        # 4. Trim the original title itself (only the non-bracketed parts)
        trimmed_original_title_without_brackets = original_title_without_brackets_for_trimming
        words = trimmed_original_title_without_brackets.split(' ')
        current_width = self._get_display_width(' '.join(words))
        while current_width > allowed_title_width:
            if not words:
                break
            words.pop()
            current_width = self._get_display_width(' '.join(words))
        trimmed_original_title_without_brackets = ' '.join(words)

        # 5. Reconstruct the title with bracketed texts
        trimmed_original_title = trimmed_original_title_without_brackets
        for bracketed_text in bracketed_texts:
            trimmed_original_title += bracketed_text

        # 6. Combine the frame and the trimmed title
        return self.title_format.format(original_title=trimmed_original_title, **kwargs)

    def generate(self, product_data: ProductData, **kwargs) -> dict:
        """
        Generates the update payload for a given product.
        """
        payload = {}
        # TODO:防呆，檢查原字串，防止重複加入字串

        # Format Title and trim it
        if self.title_format:
            payload["title"] = self._generate_and_trim_title(
                original_title=product_data.title or "", **kwargs
            )

        # Format HTML content
        if self.html_format:
            # For smartphone description
            original_sp_html = ""
            if product_data.product_description:
                original_sp_html = product_data.product_description.sp or ""
            new_sp_html = self.html_format.format(original_html=original_sp_html, **kwargs)
            payload["productDescription"] = {"sp": new_sp_html}

            # For PC sales description
            original_pc_sales_html = product_data.sales_description or ""
            new_pc_sales_html = self.html_format.format(
                original_html=original_pc_sales_html, **kwargs
            )
            payload["salesDescription"] = new_pc_sales_html

        # Create Point Campaign section
        if self.start_time and self.end_time and "point_rate" in kwargs:
            payload["pointCampaign"] = {
                "applicablePeriod": {"start": self.start_time, "end": self.end_time},
                "benefits": {"pointRate": int(kwargs["point_rate"])},
            }

        return payload
