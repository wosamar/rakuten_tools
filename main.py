import json
from pathlib import Path
from scripts.page_designs import run  # 你的 run() 函式

CONFIG_PATH = Path("./config.json")


def load_config(config_path: Path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    config = load_config(CONFIG_PATH)

    print("請選擇功能：")
    print("1. Excel → JSON")
    print("2. 生成 HTML")
    print("3. 更新 RMS 商品")
    choice = input("輸入數字：").strip()

    if choice == "1":
        run(
            shop_code=config["shop_id"],
            work_dir=Path(config["work_dir"]),
            excel_name=config.get("excel_name"),
            product_names=None,
            update_item=False,
            is_test=config.get("is_test", True)
        )
    elif choice == "2":
        run(
            shop_code=config["shop_id"],
            work_dir=Path(config["work_dir"]),
            excel_name=None,
            product_names=config.get("product_names"),
            update_item=False,
            is_test=config.get("is_test", True)
        )
    elif choice == "3":
        run(
            shop_code=config["shop_id"],
            work_dir=Path(config["work_dir"]),
            excel_name=None,
            product_names=config.get("product_names"),
            update_item=True,
            is_test=config.get("is_test", False)
        )
    else:
        print("無效選項")


if __name__ == "__main__":
    main()
