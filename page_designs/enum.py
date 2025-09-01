from enum import Enum
from pathlib import Path

from env_settings import BASE_DIR


class Template(Enum):
    PC_MAIN = "pc-main.html"
    PC_SUB = "pc-sub.html"
    MOBILE = "mobile.html"

    @property
    def path(self) -> Path:
        template_dir = BASE_DIR / "page_designs" / "templates"
        return template_dir / self.value
