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
