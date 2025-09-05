## 一、使用說明

Requirements:

- [python 3.13](https://www.python.org/downloads/)
- [poetry](https://blog.kyomind.tw/python-poetry/#%E5%AE%89%E8%A3%9D-Poetry)

`.env`

```
SERVICE_SECRET=YOUR_SECRET
LICENSE_KEY=YOUR_KEY
```

資料庫更新方式:
Alembic
`alembic revision --autogenerate -m "你的版本說明"`
`alembic upgrade head`

SQLite更新範例

```
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # 使用 batch_alter_table 來安全地刪除欄位
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('name')

def downgrade() -> None:
    # 降級時，手動將欄位加回來
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(), nullable=True))
```

## 二、專案結構

```
project_root/
│
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
```