from pathlib import Path

from pydantic.v1 import BaseSettings

# 專案根目錄
BASE_DIR = Path(__file__).parent.resolve()


class EnvSettings(BaseSettings):
    excel_dir: Path = BASE_DIR / "input" / "excel"
    json_dir: Path = BASE_DIR / "input" / "json"
    html_dir: Path = BASE_DIR / "output" / "html"

    class Config:
        env_file = ".env"  # 從.env讀取環境變數
