import pandas as pd
import json
from pathlib import Path


class ProductDocExtractor:
    def __init__(self, shop_name: str, excel_path: str):
        self.excel_path = Path(excel_path)
        self.xls = pd.ExcelFile(self.excel_path)

        self.shop_name = shop_name

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
                desc = df.iloc[i + 1, 2] if i + 1 < len(df) else None
                description = str(desc).split("\n") if pd.notna(desc) else []

            if "「商品簡短介紹」" in val:
                feat = df.iloc[i + 1, 2] if i + 1 < len(df) else None
                features = str(feat).split("\n") if pd.notna(feat) else []

            if "「商品5大賣點」" in val:
                for j in range(1, 6):
                    if i + j < len(df):
                        v = df.iloc[i + j, 2]
                        if pd.notna(v):
                            highlights.append(str(v))

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
            "image_amount": image_amount,
            "description": description if description else None,
            "features": features if features else None,
            "highlights": highlights,
            "product_info": product_info,
        }

    def extract(self) -> dict:
        sheets = [s for s in self.xls.sheet_names if "文案" in s]
        return {s: self._parse_sheet(s) for s in sheets}

    def to_json_files(self, out_dir: str):
        data = self.extract()
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        file_names = []

        for product_id, (sheet, content) in enumerate(data.items(), start=1):
            product_id = "{:02d}".format(product_id)
            filename = f"{self.shop_name}-{product_id}.json"
            file = out_path / filename

            content["shop_code"] = self.shop_name
            content["product_id"] = product_id
            with open(file, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)

            file_names.append(filename)
            print(f"已輸出：{file}")

        return file_names
