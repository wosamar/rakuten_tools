## 一、使用說明

Requirements:

- [python 3.13](https://www.python.org/downloads/)
- [poetry](https://blog.kyomind.tw/python-poetry/#%E5%AE%89%E8%A3%9D-Poetry)

`.env`

```
SERVICE_SECRET=YOUR_SECRET
LICENSE_KEY=YOUR_KEY
TENPO_NAME=TEMPO_NAME_IN_RAKUTEN
```

## 二、專案結構

```
project_root/
│
├─ handlers/              
├─ models/                   
├─ pages/     # streamlit 頁面
├─ templates/       # 資料暫存區
└─ utils/
```