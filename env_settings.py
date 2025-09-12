import base64
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings

# 專案根目錄
BASE_DIR = Path(__file__).parent.resolve()


class EnvSettings(BaseSettings):
    # Files
    output_dir: Path = BASE_DIR / "templates" / "output"
    html_tmp_dir: Path = BASE_DIR / "templates" / "html_tmp"

    # Rakuten RMS
    SERVICE_SECRET: str = "your_secret"
    LICENSE_KEY: str = "your_license_key"
    TENPO_NAME: str = "giftoftw"

    @computed_field
    @property
    def auth_token(self) -> str:
        text = f"{self.SERVICE_SECRET}:{self.LICENSE_KEY}"
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")

    class Config:
        env_file = BASE_DIR / ".env"  # 從.env讀取環境變數
        env_file_encoding = 'utf-8'
        extra = "ignore"
