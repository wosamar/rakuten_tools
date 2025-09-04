import json

import pandas as pd
from pathlib import Path

from database import Product
from handlers.database import DBHandler


class ProductDocExtractor:
    def __init__(self, shop_id: int, excel_path: str):
        self.excel_path = Path(excel_path)
        self.xls = pd.ExcelFile(self.excel_path)

        self.shop_id = shop_id
        self.db_handler = DBHandler()

    def _parse_sheet(self, sheet: str) -> dict:
        df = pd.read_excel(self.excel_path, sheet_name=sheet, header=None)

        image_amount, description, features, highlights, product_info = 0, None, None, [], {}

        for i, val in enumerate(df.iloc[:, 0]):  # A欄
            if pd.isna(val):
                continue
            val = str(val).strip()

            if "商品圖片總數" in val:
                img_amount_val = df.iloc[i, 1]  # 右欄 B 或你實際欄位
                image_amount = int(img_amount_val) if pd.notna(img_amount_val) else 0

            if "「商品詳細介紹」" in val and "圖片無文字" in val:
                description = df.iloc[i + 1, 2] if i + 1 < len(df) else None
                # description = str(desc).split("\n") if pd.notna(desc) else []

            if "「商品簡短介紹」" in val:
                features = df.iloc[i + 1, 2] if i + 1 < len(df) else None
                # features = str(feat).split("\n") if pd.notna(feat) else []

            if "「商品5大賣點」" in val:
                highlights = ""
                for j in range(1, 6):
                    if i + j < len(df):
                        v = df.iloc[i + j, 2]
                        if pd.notna(v):
                            # highlights.append(str(v))
                            highlights += f"{v}\n"

            if "「商品詳細資訊」" in val:
                for k in range(i + 1, len(df)):
                    a_val = df.iloc[k, 0]
                    c_val = df.iloc[k, 2]
                    if pd.notna(c_val):
                        key = str(a_val).split("\n")[0].strip()  # 只取換行前部分
                        value = str(c_val).strip()
                        if key in product_info:
                            product_info[key] += f" \n {value}"  # 用分隔符號接在後面
                        else:
                            product_info[key] = value

        return {
            # "image_amount": image_amount,
            "description": description if description else None,
            "feature": features if features else None,
            "highlight": highlights,
            "info": json.dumps(product_info, ensure_ascii=False),
        }

    def extract(self) -> dict:
        sheets = [s for s in self.xls.sheet_names if "文案" in s]
        return {s: self._parse_sheet(s) for s in sheets}

    def process_excel_to_db(self):
        data = self.extract()
        products = []

        for product_id, (sheet, content) in enumerate(data.items(), start=1):
            product_id = "{:02d}".format(product_id)

            content["shop_id"] = self.shop_id
            content["product_id"] = product_id

            product = self.db_handler.create_or_update(
                Product(**content),
                ["shop_id", "product_id"]
            )
            products.append(product)
            if product:
                print(f"已寫入：{vars(product)}")

        return products
