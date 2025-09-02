## 一、使用說明

Requirements:

- [python 3.13](https://www.python.org/downloads/)
- [poetry](https://blog.kyomind.tw/python-poetry/#%E5%AE%89%E8%A3%9D-Poetry)

`.env`

```
SERVICE_SECRET=YOUR_SECRET
LICENSE_KEY=YOUR_KEY
```

## 二、功能列表

### （一）下載產品圖片

- Input：產品編號列表
- Output：產品圖片列表

### （二）取得產品名稱列表

- Input：產品編號列表
- Output：產品名稱列表

### （三）HTML 生成

EXCEL→JSON→HTML→API（自動更新）

1. EXCEL前處理
    - 在A列任何一行填入「商品圖片總數」
    - 在同一行右列填入圖片總數（如：5）

   |    | A      | B   | C   |
          |----|--------|-----|-----|
   | 15 | ...    | ... | ... |
   | 16 | 商品圖片總數 | 5   |     |

2. 將 `商品資訊及文案.xlsx` 放入`input/excel/`）

## 三、專案結構

```
project_root/
│
├─ config/                   # 設定檔
│   ├─ config_excel.json
│   ├─ config_json.json
│   ├─ config_batch.json
│
├─ input/                    # 輸入檔案
│   ├─ excel/                # Excel 檔
│   │   └─ shop1.xlsx
│   ├─ json/                 # JSON 檔
│   │   ├─ shop1/ 
│   │   │   └─ shop1-01.json
│
├─ output/                   # 輸出檔案
│   ├─ html/                 # 生成的 HTML
│   │   ├─ shop1/
│   │   │   └─ shop1-01-pc.html
│   │   └─ shop2/
│   ├─ images/               # 批量下載的商品圖片
│   │   └─ 2025-09-01_1500/
│   └─ product_info/         # 批量抓取的商品資訊 JSON/CSV
│       └─ 2025-09-01_1500.json 
│
├─ scripts/                  # 程式模組
│   ├─ page_designs/         # HTML/Excel 相關模組
│   │   ├─ enum.py
│   │   ├─ excel_parser.py
│   │   ├─ html_generator.py
│   │   └─ utils.py
│   └─ items/                # RMS 相關模組
│       ├─ models.py
│       └─ update_item_handler.py
│
├─ main.py                    # CLI 主程式
└─ main.bat                   # Windows 點兩下啟動
```