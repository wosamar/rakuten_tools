from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class ProductImage(BaseModel):
    type: str
    location: str
    alt: Optional[str]


class ProductDescription(BaseModel):
    pc: Optional[str]  # PC用商品説明文(pc_main)
    sp: Optional[str]  # スマートフォン用商品説明文(mobile)


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


class ProductData(BaseModel):
    manage_number: str
    item_number: Optional[str] = None
    title: Optional[str] = None
    tagline: Optional[str] = None
    product_description: Optional[ProductDescription] = None
    sales_description: Optional[str] = None  # PC用販売説明文(pc_sub)
    images: List[ProductImage] = Field(default_factory=list)
    genre_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    standard_price: Optional[int] = None
    reference_price: Optional[int] = None

    customization_options: List[CustomizationOption] = Field(
        default_factory=list  # , alias="customizationOptions"
    )

    @classmethod
    def from_api(cls, data: dict) -> "ProductData":
        def get_reference_price(variant: dict) -> Optional[int]:
            ref = variant.get("referencePrice")
            if ref and ref.get("displayType") == "REFERENCE_PRICE":  # 有做二重價格的情況
                return int(ref.get("value", 0))
            return None

        tags = [str(tag) for tag in data.get("tags", [])]

        first_variant = next(iter(data.get("variants", {}).values()), {})
        standard_price = first_variant.get("standardPrice")
        reference_price = get_reference_price(first_variant)

        # 解析 customizationOptions
        co_raw = data.get("customizationOptions", []) or []
        customization_options = []
        for opt in co_raw:
            # selections 轉為模型
            sels = opt.get("selections")
            if sels is not None:
                sel_models = [CustomizationSelection(**s) for s in sels]
            else:
                sel_models = None

            customization_options.append(
                CustomizationOption(
                    displayName=opt.get("displayName", ""),
                    inputType=opt.get("inputType"),
                    required=opt.get("required"),
                    selections=sel_models,
                )
            )

        return cls(
            manage_number=data.get("manageNumber"),
            item_number=data.get("itemNumber"),
            title=data.get("title"),
            tagline=data.get("tagline"),
            product_description=ProductDescription(
                pc=data.get("productDescription", {}).get("pc"),
                sp=data.get("productDescription", {}).get("sp")
            ) if data.get("productDescription") else None,
            sales_description=data.get("salesDescription"),
            images=[ProductImage(**img) for img in data.get("images", [])],
            genre_id=data.get("genreId"),
            tags=tags,
            standard_price=standard_price,
            reference_price=reference_price,
            customizationOptions=customization_options
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
            desc = {}
            if self.product_description.pc:
                desc["pc"] = self.product_description.pc
            if self.product_description.sp:
                desc["sp"] = self.product_description.sp
            if desc:
                payload["productDescription"] = desc
        if self.sales_description:
            payload["salesDescription"] = self.sales_description
        if self.images:
            payload["images"] = [img.model_dump() for img in self.images]
        if self.genre_id:
            payload["genreId"] = self.genre_id
        if self.tags:
            payload["tags"] = self.tags

        if self.customization_options:
            payload["customizationOptions"] = [opt.to_api() for opt in self.customization_options]
        return payload
