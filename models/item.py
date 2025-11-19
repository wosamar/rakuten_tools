from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict


class ProductImage(BaseModel):
    type: str
    location: str
    alt: Optional[str]


class ProductDescription(BaseModel):
    pc: Optional[str] = None  # PC用商品説明文(pc_main)
    sp: Optional[str] = None  # スマートフォン用商品説明文(mobile)


class DisplayTypeEnum(str, Enum):
    REFERENCE_PRICE = "REFERENCE_PRICE"
    SHOP_SETTING = "SHOP_SETTING"
    OPEN_PRICE = "OPEN_PRICE"


class ReferencePrice(BaseModel):
    display_type: DisplayTypeEnum = Field(..., alias="displayType")
    type: Optional[int] = None
    value: Optional[str] = None

    @model_validator(mode="after")
    def validate_reference_price(self):
        if self.display_type == DisplayTypeEnum.REFERENCE_PRICE:
            if self.type is None:
                raise ValueError("type is required when displayType is REFERENCE_PRICE")
            if self.type != 4 and self.value is None:
                raise ValueError("value is required when displayType is REFERENCE_PRICE and type is not 4")
        return self


# === Customization 定義 ===

class CustomizationInputType(str, Enum):
    SINGLE_SELECTION = "SINGLE_SELECTION"  # セレクトボックス
    MULTIPLE_SELECTION = "MULTIPLE_SELECTION"  # チェックボックス
    FREE_TEXT = "FREE_TEXT"  # フリーテキスト


class CustomizationSelection(BaseModel):
    display_value: str = Field(..., alias="displayValue", max_length=32)

    # 允許除 ":" "<" ">" 與 HTML 標籤外的大多數字元（API 規格說明）
    # 若要嚴格阻擋，可在此加 regex 驗證

    def to_api(self) -> dict:
        return {"displayValue": self.display_value}


class CustomizationOption(BaseModel):
    display_name: str = Field(..., alias="displayName", max_length=255)
    input_type: CustomizationInputType = Field(..., alias="inputType")
    required: Optional[bool] = Field(default=None, alias="required")
    selections: Optional[List[CustomizationSelection]] = Field(
        default=None, alias="selections"
    )

    @model_validator(mode="after")
    def _validate_selections_rules(self):
        """
        規則：
        - SINGLE_SELECTION/MULTIPLE_SELECTION：selections 為必填
            - SINGLE_SELECTION 最多 100
            - MULTIPLE_SELECTION 最多 40
        - FREE_TEXT：selections 不可存在（或將其忽略）
        """
        if self.input_type in (
                CustomizationInputType.SINGLE_SELECTION,
                CustomizationInputType.MULTIPLE_SELECTION,
        ):
            if not self.selections or len(self.selections) == 0:
                raise ValueError("selections is required when inputType is SINGLE_SELECTION or MULTIPLE_SELECTION")

            limit = 100 if self.input_type == CustomizationInputType.SINGLE_SELECTION else 40
            if len(self.selections) > limit:
                raise ValueError(f"selections exceeds max length: {limit}")
        else:
            # FREE_TEXT 不應附 selections
            if self.selections:
                # 也可選擇自動清空： self.selections = None
                raise ValueError("selections must be omitted when inputType is FREE_TEXT")
        return self

    def to_api(self) -> dict:
        data = {
            "displayName": self.display_name,
            "inputType": self.input_type.value,
        }
        if self.required is not None:
            data["required"] = self.required
        if self.selections is not None:
            data["selections"] = [s.to_api() for s in self.selections]
        return data


class ApplicablePeriod(BaseModel):
    start: str  # ポイント変倍率適用期間（開始日時）
    end: str  # ポイント変倍率適用期間（終了日時）


class Benefits(BaseModel):
    point_rate: int = Field(..., alias="pointRate")  # ポイント変倍率


class PointCampaign(BaseModel):
    applicable_period: ApplicablePeriod = Field(..., alias="applicablePeriod")  # ポイント変倍適用期間
    benefits: Benefits  # ポイント情報


class PurchasablePeriod(BaseModel):
    start: str  # 販売開始日時
    end: str  # 販売終了日時


class ProductData(BaseModel):
    manage_number: str  # 商品管理番号（商品URL）
    item_number: Optional[str] = None  # 商品番号
    title: Optional[str] = None  # 商品名
    tagline: Optional[str] = None
    product_description: Optional[ProductDescription] = None  # 其他說明文
    sales_description: Optional[str] = None  # PC用販売説明文(pc_sub)
    images: List[ProductImage] = Field(default_factory=list)
    genre_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    standard_price: Optional[int] = None
    reference_price_info: Optional[ReferencePrice] = Field(default=None, alias="referencePrice")
    point_campaign: Optional[PointCampaign] = Field(default=None, alias="pointCampaign")  # ポイント変倍情報
    purchasable_period: Optional[PurchasablePeriod] = None  # 販売期間指定
    is_hidden: bool = False  # 倉庫指定

    # TODO:自動產生別名
    customization_options: List[CustomizationOption] = Field(
        default_factory=list, alias="customizationOptions"
    )

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_api(cls, data: dict) -> "ProductData":
        """
        Creates a ProductData instance from a raw API dictionary.
        Handles both detailed (get_item) and summary (search_item) formats.
        """
        # Handle nested product description from detailed view, fallback to flat view
        if "productDescription" in data and isinstance(data["productDescription"], dict):
            product_desc_data = data["productDescription"]
            pc_desc = product_desc_data.get("pc", "")
            sp_desc = product_desc_data.get("sp", "")
        else:
            # Fallback for search results or other flat structures
            pc_desc = data.get("descriptionForPC", "")
            sp_desc = data.get("descriptionForSmartPhone", "")

        # Use salesDescription if present, else fallback to pc_desc
        sales_desc = data.get("salesDescription") or pc_desc

        tags = [str(tag) for tag in data.get("tags", [])]

        first_variant = next(iter(data.get("variants", {}).values()), {})
        standard_price = first_variant.get("standardPrice")
        
        reference_price_data = first_variant.get("referencePrice")
        reference_price_info = ReferencePrice(**reference_price_data) if reference_price_data else None

        co_raw = data.get("customizationOptions", []) or []
        customization_options = []
        for opt in co_raw:
            sels = opt.get("selections")
            sel_models = [CustomizationSelection(**s) for s in sels] if sels is not None else None
            customization_options.append(
                CustomizationOption(
                    displayName=opt.get("displayName", ""),
                    inputType=opt.get("inputType"),
                    required=opt.get("required"),
                    selections=sel_models,
                )
            )

        return cls(
            manage_number=data.get("manageNumber", ""),
            item_number=data.get("itemNumber"),
            title=data.get("title"),
            tagline=data.get("tagline"),
            product_description=ProductDescription(pc=pc_desc, sp=sp_desc),
            sales_description=sales_desc,
            images=[ProductImage(**img) for img in data.get("images", [])],
            genre_id=data.get("genreId"),
            tags=tags,
            standard_price=standard_price,
            reference_price_info=reference_price_info,
            customization_options=customization_options,
            point_campaign=PointCampaign(**data['pointCampaign']) if 'pointCampaign' in data else None,
            is_hidden=data.get("hideItem", False)
        )

    def to_patch_payload(self) -> dict:
        """輸出給 patchItem，用來部分更新（略過 None 欄位）"""
        payload = {}
        if self.item_number:
            payload["itemNumber"] = self.item_number
        if self.title:
            payload["title"] = self.title
        if self.tagline:
            payload["tagline"] = self.tagline
        if self.product_description:
            payload["productDescription"] = {"sp": self.product_description}
        if self.sales_description:
            payload["salesDescription"] = self.sales_description
        if self.images:
            payload["images"] = [img.model_dump() for img in self.images]
        if self.genre_id:
            payload["genreId"] = self.genre_id
        if self.tags:
            payload["tags"] = self.tags
        if self.point_campaign:
            payload["pointCampaign"] = self.point_campaign.model_dump(by_alias=True)

        if self.customization_options:
            payload["customizationOptions"] = [opt.to_api() for opt in self.customization_options]
        return payload

    def to_csv(self) -> dict:
        """
        Returns a dictionary of product data flattened for CSV output.
        """
        csv_data = {
            "商品管理番号（商品URL）": self.manage_number,
            "商品番号": self.item_number or "",
            "商品名": self.title or "",
            "通常購入販売価格": self.standard_price or 0,
            "PC用商品説明文": self.product_description.pc if self.product_description else "",
            "スマートフォン用商品説明文": self.product_description.sp if self.product_description else "",
            "PC用販売説明文": self.sales_description or "",
            "ポイント変倍率": self.point_campaign.benefits.point_rate if self.point_campaign and self.point_campaign.benefits else 0,
            "ポイント変倍率適用期間（開始日時）": self.point_campaign.applicable_period.start if self.point_campaign and self.point_campaign.applicable_period else "",
            "ポイント変倍率適用期間（終了日時）": self.point_campaign.applicable_period.end if self.point_campaign and self.point_campaign.applicable_period else "",
        }
        return csv_data
