import json
import re
from io import BytesIO

import pandas as pd

from database import Product, Image, Shop
from handlers.database import DBHandler


class ProductExcelParser:
    def __init__(self, shop_id: int, excel_bytes: bytes):
        self.db = DBHandler()

        self.shop = self.db.get(Shop, **{"id": shop_id})
        self.xls = self.xls = pd.ExcelFile(BytesIO(excel_bytes))
        self.known_headers = [
            "商品圖片名稱",
            "「商品詳細介紹」<圖片含文字>",
            "「商品詳細介紹」<圖片無文字>",
            "「商品簡短介紹」<一段100字以內文字>",
            "「商品5大賣點」<每項一段文字即可>",
            "「商品詳細資訊」"
        ]

    def collect_block(self, df: pd.DataFrame, start_idx: int, col: int = 2) -> list[str]:
        result = []
        for i in range(start_idx + 1, len(df)):
            val = df.iloc[i, 0]
            if pd.isna(val) or str(val).strip() in self.known_headers:
                break
            cell = df.iloc[i, col]
            if pd.notna(cell):
                result.append(str(cell).strip())
        return result

    def sheet_to_sequence(self, sheet_name: str) -> str:
        """將 sheet_name 轉為 product_id，只取數字部分"""
        num_match = re.search(r"\d+", sheet_name)
        num_part = num_match.group() if num_match else sheet_name
        return f"{num_part}"

    def parse_sheet(self, sheet_name: str) -> dict:
        df = pd.read_excel(self.xls, sheet_name=sheet_name, header=None)
        description, features, highlights, images = None, None, "", []
        product_info = {}

        for i, val in enumerate(df.iloc[:, 0]):
            val = str(val).strip()
            if val == "商品圖片名稱":
                images = self.collect_block(df, i, col=0)
            elif "「商品詳細介紹」<圖片含文字>" in val:
                description = "\n".join(self.collect_block(df, i))
            elif "「商品詳細介紹」<圖片無文字>" in val:
                description = "\n".join(self.collect_block(df, i))
            elif "「商品簡短介紹」" in val:
                features = "\n".join(self.collect_block(df, i))
            elif "「商品5大賣點」" in val:
                highlights = "\n".join(self.collect_block(df, i))
            elif "「商品詳細資訊」" in val:
                for k in range(i + 1, len(df)):
                    a_val = df.iloc[k, 0]
                    c_val = df.iloc[k, 2]
                    if str(a_val).strip() in self.known_headers:
                        break
                    if not pd.isna(c_val):
                        key = str(a_val).split("\n")[0].strip()
                        value = str(c_val).strip()
                        if key in product_info:
                            product_info[key] += f"\n{value}"
                        else:
                            product_info[key] = value

        p = Product(
            shop_id=self.shop.id,
            sequence=self.sheet_to_sequence(sheet_name),
            description=description or "",
            feature=features or "",
            highlight=highlights or "",
            info=json.dumps(product_info, ensure_ascii=False)
        ).__dict__
        p["images"] = [Image(file_name=n).__dict__ for n in images]
        return p

    def parse_all_sheets(self) -> list[dict]:
        products = []
        for sheet in self.xls.sheet_names:
            if "文案" in sheet:
                products.append(self.parse_sheet(sheet))
        return products
