from typing import Dict, List, Optional, Set, Tuple

from pydantic import BaseModel

from handlers.payload_generator import CampaignPayloadGenerator
from models.item import ProductData


class CampaignConfig(BaseModel):
    """A model to hold all configuration for the campaign update flow."""

    point_title_format: str
    point_html_format: str
    start_time: str
    end_time: str
    feature_title_format: str
    feature_html_format: str
    no_event_html_format: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)

        # Process point_title_format
        if "{original_title}" not in self.point_title_format:
            self.point_title_format += " {original_title}"

        # Process point_html_format
        if "{original_html}" not in self.point_html_format:
            self.point_html_format += "{original_html}"

        # Process feature_title_format
        if "{original_title}" not in self.feature_title_format:
            self.feature_title_format = "{original_title}" + self.feature_title_format

        # Process feature_html_format
        if "{original_html}" not in self.feature_html_format:
            self.feature_html_format += "{original_html}"

        # Process no_event_html_format
        if self.no_event_html_format and "{original_html}" not in self.no_event_html_format:
            self.no_event_html_format += "{original_html}"


class CampaignUpdateFlow:
    """
    A flow to process campaign data and generate the final API payloads for updates.
    It receives all necessary product data and campaign configurations upon execution.
    """

    def __init__(self):
        """Initializes the flow."""
        self.original_items_cache: Dict[str, ProductData] = {}

    def execute(
        self,
        all_products: List[ProductData],
        config: CampaignConfig,
        point_campaigns: List[Dict],
        feature_campaign: Dict,
    ) -> Dict[str, Dict]:
        """
        Executes the workflow by categorizing items and generating payloads.

        Args:
            all_products: A list of all product data objects.
            config: A configuration object containing all templates and times.
            point_campaigns: A list of point campaign dicts.
            feature_campaign: A single feature campaign dict.

        Returns:
            A dictionary where keys are manageNumbers and values are the generated payloads.
        """
        # 1. Initialize internal caches and lookup maps for quick data access.
        self.original_items_cache = {
            p.manage_number: p for p in all_products if p.manage_number
        }
        item_to_point_rate, item_to_campaign_code = self._build_lookup_maps(
            point_campaigns, feature_campaign
        )

        # TODO: 修正字數計算問題
        # 2. Categorize all items into mutually exclusive groups.
        visible_item_ids = {
            k
            for k, v in self.original_items_cache.items()
            if not v.is_hidden
        }
        print(len(visible_item_ids))
        categories = self._categorize_items(
            visible_ids=visible_item_ids,
            point_ids=set(item_to_point_rate.keys()),
            feature_ids=set(item_to_campaign_code.keys()),
        )

        # 3. Process each category and generate the corresponding payloads.
        all_payloads = {}
        all_payloads.update(
            self._process_point_feature_items(
                categories["point_and_feature"],
                config,
                item_to_point_rate,
                item_to_campaign_code,
            )
        )
        all_payloads.update(
            self._process_point_only_items(
                categories["point_only"], config, item_to_point_rate
            )
        )
        all_payloads.update(
            self._process_feature_only_items(
                categories["feature_only"], config, item_to_campaign_code
            )
        )
        all_payloads.update(
            self._process_no_event_items(categories["no_event"], config)
        )

        return all_payloads

    def _build_lookup_maps(
        self, point_campaigns: List[Dict], feature_campaign: Dict
    ) -> Tuple[Dict[str, int], Dict[str, str]]:
        """Creates dictionaries mapping item IDs to their campaign-specific values."""
        item_to_point_rate = {
            item: campaign["point_rate"]
            for campaign in point_campaigns
            for item in campaign.get("items", [])
        }
        campaign_code = feature_campaign.get("campaign_code", "")
        item_to_campaign_code = {
            item: campaign_code for item in feature_campaign.get("items", [])
        }
        return item_to_point_rate, item_to_campaign_code

    def _categorize_items(
        self,
        visible_ids: Set[str],
        point_ids: Set[str],
        feature_ids: Set[str],
    ) -> Dict[str, Set[str]]:
        """Sorts item IDs into four mutually exclusive categories."""
        point_and_feature_ids = point_ids.intersection(feature_ids)
        point_only_ids = point_ids - feature_ids
        feature_only_ids = feature_ids - point_ids
        campaign_item_ids = point_ids.union(feature_ids)
        no_event_ids = visible_ids - campaign_item_ids

        return {
            "point_and_feature": point_and_feature_ids,
            "point_only": point_only_ids,
            "feature_only": feature_only_ids,
            "no_event": no_event_ids,
        }

    def _process_point_feature_items(
        self,
        item_ids: Set[str],
        config: CampaignConfig,
        item_to_point_rate: Dict[str, int],
        item_to_campaign_code: Dict[str, str],
    ) -> Dict[str, Dict]:
        """Processes items that are in both a point and a feature campaign."""
        if not item_ids:
            return {}

        point_title_prefix = config.point_title_format.split("{original_title}")[0]
        feature_title_suffix = config.feature_title_format.split("{original_title}")[1]
        merged_title_format = (
            f"{point_title_prefix}{{original_title}}{feature_title_suffix}"
        )

        generator = CampaignPayloadGenerator(
            title_format=merged_title_format,
            html_format=config.point_html_format,
            start_time=config.start_time,
            end_time=config.end_time,
        )
        payloads = {}
        for item_id in item_ids:
            original_data = self.original_items_cache.get(item_id)
            if original_data:
                payload = generator.generate(
                    original_data,
                    point_rate=item_to_point_rate[item_id],
                    campaign_code=item_to_campaign_code[item_id],
                )
                if payload:
                    payloads[item_id] = payload
        return payloads

    def _process_point_only_items(
        self,
        item_ids: Set[str],
        config: CampaignConfig,
        item_to_point_rate: Dict[str, int],
    ) -> Dict[str, Dict]:
        """Processes items that are only in a point campaign."""
        if not item_ids:
            return {}

        generator = CampaignPayloadGenerator(
            title_format=config.point_title_format,
            html_format=config.point_html_format,
            start_time=config.start_time,
            end_time=config.end_time,
        )
        payloads = {}
        for item_id in item_ids:
            original_data = self.original_items_cache.get(item_id)
            if original_data:
                payload = generator.generate(
                    original_data, point_rate=item_to_point_rate[item_id]
                )
                if payload:
                    payloads[item_id] = payload
        return payloads

    def _process_feature_only_items(
        self,
        item_ids: Set[str],
        config: CampaignConfig,
        item_to_campaign_code: Dict[str, str],
    ) -> Dict[str, Dict]:
        """Processes items that are only in a feature campaign."""
        if not item_ids:
            return {}

        generator = CampaignPayloadGenerator(
            title_format=config.feature_title_format,
            html_format=config.feature_html_format,
        )
        payloads = {}
        for item_id in item_ids:
            original_data = self.original_items_cache.get(item_id)
            if original_data:
                payload = generator.generate(
                    original_data, campaign_code=item_to_campaign_code[item_id]
                )
                if payload:
                    payloads[item_id] = payload
        return payloads

    def _process_no_event_items(
        self, item_ids: Set[str], config: CampaignConfig
    ) -> Dict[str, Dict]:
        """Processes items that are not in any campaign."""
        if not item_ids or not config.no_event_html_format:
            return {}

        generator = CampaignPayloadGenerator(html_format=config.no_event_html_format)
        payloads = {}
        for item_id in item_ids:
            original_data = self.original_items_cache.get(item_id)
            if original_data:
                payload = generator.generate(original_data)
                if payload:
                    payloads[item_id] = payload
        return payloads

    def _process_point_events(self, data: Dict) -> Dict[str, Dict]:
        if not data.get("campaigns"):
            return {}

        payloads = {}
        generator = CampaignPayloadGenerator(
            title_format=data.get("title_format"),
            html_format=data.get("html_format"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
        )

        for campaign in data["campaigns"]:
            point_rate = campaign.get("point_rate")
            for item_id in campaign.get("items", []):
                original_data = self.original_items_cache.get(item_id)
                if original_data and point_rate is not None:
                    payload = generator.generate(original_data, point_rate=point_rate)
                    payloads[item_id] = payload
        return payloads

    def _process_feature_events(self, data: Dict) -> Dict[str, Dict]:
        if not data.get("campaigns"):
            return {}

        payloads = {}
        generator = CampaignPayloadGenerator(
            title_format=data.get("title_format"),
            html_format=data.get("html_format"),
        )

        for campaign in data["campaigns"]:
            campaign_code = campaign.get("campaign_code", "")
            for item_id in campaign.get("items", []):
                original_data = self.original_items_cache.get(item_id)
                if original_data:
                    payload = generator.generate(
                        original_data, campaign_code=campaign_code
                    )
                    payloads[item_id] = payload
        return payloads

    def _process_no_events(self, data: Dict) -> Dict[str, Dict]:
        if not data.get("campaigns"):
            return {}

        payloads = {}
        generator = CampaignPayloadGenerator(html_format=data.get("html_format"))

        for campaign in data["campaigns"]:
            for item_id in campaign.get("items", []):
                original_data = self.original_items_cache.get(item_id)
                if original_data:
                    payload = generator.generate(original_data)
                    payloads[item_id] = payload
        return payloads
