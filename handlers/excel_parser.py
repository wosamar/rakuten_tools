import json
import re
from io import BytesIO

import pandas as pd

from env_settings import EnvSettings

env_settings = EnvSettings()


class ProductExcelParser:
    def __init__(self, shop_code: str, excel_bytes: bytes):
        self.xls = self.xls = pd.ExcelFile(BytesIO(excel_bytes))
        self.known_headers = [
            "商品圖片名稱",
            "「商品詳細介紹」<圖片含文字>",
            "「商品詳細介紹」<圖片無文字>",
            "「商品簡短介紹」<一段100字以內文字>",
            "「商品5大賣點」<每項一段文字即可>",
            "「商品詳細資訊」"
        ]

        # 商品圖片連結
        shop_name = shop_code.split("-")[-1]
        self.cabinet_prefix = f"https://image.rakuten.co.jp/{env_settings.TENPO_NAME}/cabinet/{shop_name}"
        # 詳細資訊欄位名對照
        product_info_dict_path = env_settings.tmp_dir / "product_info_td.json"
        with open(product_info_dict_path, "r", encoding="utf-8") as f:
            self.field_mapping = json.load(f)

    def collect_block(self, df: pd.DataFrame, start_idx: int, col: int = 2) -> list[str]:
        result = []
        for i in range(start_idx + 1, len(df)):
            val = df.iloc[i, 0]
            if any(header in str(val).strip() for header in self.known_headers):
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
        if df.shape[1] < 3:
            return {}

        # 清掉全形空白和零寬空白
        df = df.apply(
            lambda col: col.map(
                lambda x: str(x).replace("\u200b", "").strip() if not pd.isna(x) else x
            ),
            axis=0
        )

        description, feature, highlight, product_info, image_infos, image_descriptions = None, None, "", {}, [], []
        image_infos = []
        for i, val in enumerate(df.iloc[:, 0]):
            val = str(val).strip()
            if "「商品詳細介紹」<圖片含文字>" in val:
                for k in range(i + 1, len(df)):
                    a_val = df.iloc[k, 0]
                    if (any(header in str(a_val).strip() for header in self.known_headers) or
                            pd.isna(a_val) or
                            not str(a_val).lower().endswith((".jpg", ".jpeg", ".png"))):
                        break

                    c_val = df.iloc[k, 2] if df.shape[1] > 2 else None
                    d_val = df.iloc[k, 3] if df.shape[1] > 3 else None

                    key = str(a_val).split("\n")[0].strip()
                    description_val = None if pd.isna(c_val) else str(c_val).strip()
                    link_val = None if pd.isna(d_val) else str(d_val).strip()

                    image_infos.append(dict(
                        image_url=f"{self.cabinet_prefix}/{key}",
                        description=description_val,
                        link=link_val
                    ))

            elif "「商品詳細介紹」<圖片無文字>" in val:
                description = "\n".join(self.collect_block(df, i))
            elif "「商品簡短介紹」" in val:
                feature = "\n".join(self.collect_block(df, i))
            elif "「商品5大賣點」" in val:
                highlight = "\n".join(self.collect_block(df, i))
            elif "「商品詳細資訊」" in val:
                for k in range(i + 1, len(df)):
                    a_val = df.iloc[k, 0]
                    c_val = df.iloc[k, 2]
                    if any(header in str(a_val).strip() for header in self.known_headers):
                        break
                    if not pd.isna(c_val):
                        key = str(a_val).split("\n")[0].strip()
                        key = self.field_mapping.get(key, key)

                        value = str(c_val).strip()
                        if key in product_info:
                            product_info[key] += f"\n{value}"
                        else:
                            product_info[key] = value
        return {
            "sequence": self.sheet_to_sequence(sheet_name),
            "image_infos": image_infos,
            "description": description,
            "feature": feature,
            "highlight": highlight,
            "product_info": product_info
        }

    def parse_all_sheets(self) -> list[dict]:
        products = []
        for sheet in self.xls.sheet_names:
            if "文案" in sheet:
                if product := self.parse_sheet(sheet):
                    products.append(product)
        return products
