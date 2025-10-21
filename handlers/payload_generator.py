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

    def _apply_format_if_needed(
        self,
        original_content: str,
        format_string: str,
        placeholder: str,
        formatter_func=None, # For titles, this will be _generate_and_trim_title
        **kwargs
    ) -> str:
        """
        Checks if original_content already contains the formatted prefix/suffix.
        If so, returns original_content. Otherwise, applies the format_string.
        """
        if not format_string:
            return original_content

        parts = re.split(re.escape(placeholder), format_string)
        prefix_template = parts[0]
        suffix_template = parts[1] if len(parts) > 1 else ""

        # Create a temporary kwargs dict without the placeholder to format prefix/suffix
        temp_kwargs = {k: v for k, v in kwargs.items() if k != placeholder.strip("{}")}
        
        actual_prefix = prefix_template.format(**temp_kwargs)
        actual_suffix = suffix_template.format(**temp_kwargs)

        if original_content.startswith(actual_prefix) and original_content.endswith(actual_suffix):
            return original_content
        else:
            if formatter_func:
                return formatter_func(original_title=original_content, **kwargs)
            else:
                return format_string.format(original_html=original_content, **kwargs)

    def generate(self, product_data: ProductData, **kwargs) -> dict:
        """
        Generates the update payload for a given product.
        """
        payload = {}

        original_title_content = product_data.title or ""
        original_sp_html_content = product_data.product_description.sp if product_data.product_description else ""
        original_pc_sales_html_content = product_data.sales_description or ""

        # --- Title Duplication Check and Formatting ---
        if self.title_format:
            payload["title"] = self._apply_format_if_needed(
                original_content=original_title_content,
                format_string=self.title_format,
                placeholder="{original_title}",
                formatter_func=self._generate_and_trim_title,
                **kwargs
            )

        # --- HTML Content Duplication Check and Formatting ---
        if self.html_format:
            # For smartphone description
            new_sp_html = self._apply_format_if_needed(
                original_content=original_sp_html_content,
                format_string=self.html_format,
                placeholder="{original_html}",
                **kwargs
            )
            payload["productDescription"] = {"sp": new_sp_html}

            # For PC sales description
            new_pc_sales_html = self._apply_format_if_needed(
                original_content=original_pc_sales_html_content,
                format_string=self.html_format,
                placeholder="{original_html}",
                **kwargs
            )
            payload["salesDescription"] = new_pc_sales_html

        # Create Point Campaign section
        if self.start_time and self.end_time and "point_rate" in kwargs:
            payload["pointCampaign"] = {
                "applicablePeriod": {"start": self.start_time, "end": self.end_time},
                "benefits": {"pointRate": int(kwargs["point_rate"])},
            }

        return payload
