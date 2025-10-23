import unicodedata
import re
from typing import Optional, Dict
from models.item import ProductData


class BaseContentGenerator:
    """
    Base class for content generators, providing common utility methods.
    """

    @staticmethod
    def _get_display_width(text: str) -> int:
        width = 0
        for char in text:
            if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
                width += 2
            else:
                width += 1
        return width

    def _apply_format_if_needed(
            self,
            original_content: str,
            format_string: str,
            placeholder: str,
            formatter_func=None,
            **kwargs
    ) -> str:
        """
        Checks if original_content already contains the formatted prefix/suffix.
        If so, returns original_content. Otherwise, applies the format_string.
        """
        if not format_string:
            return original_content

        processed_content = original_content
        if formatter_func:
            processed_content = formatter_func(original_content=original_content, **kwargs)



        # Define actual_prefix and actual_suffix here, before they are used
        parts = re.split(re.escape(placeholder), format_string)
        prefix_template = parts[0]
        suffix_template = parts[1] if len(parts) > 1 else ""

        temp_kwargs = {k: v for k, v in kwargs.items() if k != placeholder.strip("{}")}

        actual_prefix = prefix_template.format(**temp_kwargs)
        actual_suffix = suffix_template.format(**temp_kwargs)

        if processed_content.startswith(actual_prefix) and processed_content.endswith(actual_suffix):
            return processed_content
        else:
            return format_string.format(original_title=processed_content, original_html=processed_content, **kwargs)


class TitleGenerator(BaseContentGenerator):
    """
    Generates and trims product titles based on a format string.
    """

    def __init__(self, title_format: Optional[str] = None, max_width: int = 255):
        self.title_format = title_format
        self.max_width = max_width

    def _generate_and_trim_title(
            self, original_content: str, **kwargs
    ) -> str:
        """
        Generates a title by first trimming the original_content to fit within
        the campaign text frame, then combines them.
        max_width = 半形 255 = 全形 127
        """
        if not self.title_format:
            return original_content

        # 1. Extract bracketed text and replace with placeholders
        bracketed_texts_map = {}
        placeholder_counter = 0
        def replace_bracketed(match):
            nonlocal placeholder_counter
            placeholder = f"__BRACKET_{placeholder_counter}__"
            bracketed_texts_map[placeholder] = match.group(0)
            placeholder_counter += 1
            return placeholder

        # Add a space before 【 to separate it from the previous word, if there's no space.
        content_with_space_before_bracket = re.sub(r'([^\s])(【)', r'\1 \2', original_content)
        content_with_placeholders = re.sub(r'【.*?】', replace_bracketed, content_with_space_before_bracket)

        # 2. Calculate the width of the "frame" (the format string without original_title)
        temp_title_for_frame = self.title_format.replace("{original_title}", "")
        frame_text = temp_title_for_frame.format(original_title="", **kwargs)
        frame_width = self._get_display_width(frame_text)

        # 3. Determine the max allowed width for the original title (including placeholders)
        allowed_title_width = self.max_width - frame_width

        # 4. Trim the content by removing non-placeholder words from the end
        words = content_with_placeholders.split(' ')
        words = [w for w in words if w]  # remove empty strings

        current_width = self._get_display_width(' '.join(words))

        while current_width > allowed_title_width:
            if not words:
                break

            # Find the last word that is NOT a placeholder
            last_trimmable_word_index = -1
            for i in range(len(words) - 1, -1, -1):
                if not words[i].startswith('__BRACKET_'):
                    last_trimmable_word_index = i
                    break

            if last_trimmable_word_index != -1:
                words.pop(last_trimmable_word_index)
            else:
                # All remaining words are placeholders, and it's still too long.
                # Pop the last one to avoid an infinite loop.
                words.pop()

            # Recalculate current_width with actual bracketed texts for accurate trimming
            temp_content_for_width_calc = ' '.join(words)
            for placeholder, original_text in bracketed_texts_map.items():
                temp_content_for_width_calc = temp_content_for_width_calc.replace(placeholder, original_text)
            current_width = self._get_display_width(temp_content_for_width_calc)

        trimmed_content_with_placeholders = ' '.join(words)

        # 5. Reconstruct the title by replacing placeholders with original bracketed texts
        trimmed_original_title = trimmed_content_with_placeholders
        for placeholder, original_text in bracketed_texts_map.items():
            trimmed_original_title = trimmed_original_title.replace(placeholder, original_text)

        # 6. Return only the trimmed content, without applying the format string yet
        return trimmed_original_title

    def generate_title_payload(self, original_title_content: str, **kwargs) -> Dict:
        payload = {}
        if self.title_format:
            payload["title"] = self._apply_format_if_needed(
                original_content=original_title_content,
                format_string=self.title_format,
                placeholder="{original_title}",
                formatter_func=self._generate_and_trim_title,
                **kwargs
            )
        return payload


class HtmlGenerator(BaseContentGenerator):
    """
    Generates HTML content for product descriptions and sales descriptions.
    """

    def __init__(self, html_format: Optional[str] = None):
        self.html_format = html_format

    def generate_html_payload(self, product_data: ProductData, **kwargs) -> Dict:
        payload = {}
        if self.html_format:
            original_sp_html_content = product_data.product_description.sp if product_data.product_description else ""
            original_pc_sales_html_content = product_data.sales_description or ""

            new_sp_html = self._apply_format_if_needed(
                original_content=original_sp_html_content,
                format_string=self.html_format,
                placeholder="{original_html}",
                **kwargs
            )
            payload["productDescription"] = {"sp": new_sp_html}

            new_pc_sales_html = self._apply_format_if_needed(
                original_content=original_pc_sales_html_content,
                format_string=self.html_format,
                placeholder="{original_html}",
                **kwargs
            )
            payload["salesDescription"] = new_pc_sales_html
        return payload


class PointCampaignGenerator:
    """
    Generates the payload for point campaign information.
    """

    def __init__(
            self,
            start_time: Optional[str] = None,
            end_time: Optional[str] = None,
    ):
        self.start_time = start_time
        self.end_time = end_time

    def generate_point_campaign_payload(self, **kwargs) -> Dict:
        payload = {}
        if self.start_time and self.end_time and "point_rate" in kwargs:
            payload["pointCampaign"] = {
                "applicablePeriod": {"start": self.start_time, "end": self.end_time},
                "benefits": {"pointRate": int(kwargs["point_rate"])},
            }
        return payload


class CampaignPayloadGenerator:
    """
    Orchestrates the generation of a complete product update payload
    by delegating to specialized generators.
    """

    def __init__(
            self,
            title_format: Optional[str] = None,
            html_format: Optional[str] = None,
            start_time: Optional[str] = None,
            end_time: Optional[str] = None,
            max_width: int = 255
    ):
        self.title_generator = TitleGenerator(title_format, max_width)
        self.html_generator = HtmlGenerator(html_format)
        self.point_campaign_generator = PointCampaignGenerator(start_time, end_time)

    def generate(self, product_data: ProductData, **kwargs) -> Dict:
        """
        Generates the update payload for a given product.
        """
        payload = {}

        payload.update(self.title_generator.generate_title_payload(
            original_title_content=product_data.title or "",
            **kwargs
        ))

        payload.update(self.html_generator.generate_html_payload(
            product_data=product_data,
            **kwargs
        ))

        payload.update(self.point_campaign_generator.generate_point_campaign_payload(
            **kwargs
        ))

        return payload
