import base64
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings

# 專案根目錄
BASE_DIR = Path(__file__).parent.resolve()


class EnvSettings(BaseSettings):
    DB_NAME: str = "RakutenRepo"

    DB_USER: str = "root"
    DB_PASSWORD: str = "root"

    DB_HOST: str = "127.0.0.1"
    DB_PORT: str = "3306"
    USE_SQLITE: bool = False

    excel_dir: Path = BASE_DIR / "input" / "excel"  # 待刪除
    json_dir: Path = BASE_DIR / "input" / "json"  # 待刪除
    html_dir: Path = BASE_DIR / "output" / "html"  # 待刪除
    output_dir: Path = BASE_DIR / "templates" / "output"
    html_tmp_dir: Path = BASE_DIR / "templates" / "html"

    SERVICE_SECRET: str = "your_secret"
    LICENSE_KEY: str = "your_license_key"

    @computed_field
    @property
    def auth_token(self) -> str:
        text = f"{self.SERVICE_SECRET}:{self.LICENSE_KEY}"
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    class Config:
        env_file = BASE_DIR / ".env"  # 從.env讀取環境變數
        env_file_encoding = 'utf-8'
