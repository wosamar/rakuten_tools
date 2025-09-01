from typing import List, Optional
from pydantic import BaseModel, Field


class ProductImage(BaseModel):
    type: str
    location: str
    alt: Optional[str]


class ProductDescription(BaseModel):
    pc: Optional[str]
    sp: Optional[str]


class ProductData(BaseModel):
    manage_number: str
    item_number: Optional[str] = None
    title: Optional[str] = None
    tagline: Optional[str] = None
    product_description: Optional[ProductDescription] = None
    sales_description: Optional[str] = None
    images: List[ProductImage] = Field(default_factory=list)
    genre_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict) -> "ProductData":
        """把 RMS getItem 回傳的 JSON 轉成 ProductInfo"""
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
            tags=data.get("tags", []),
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
        return payload
