import base64
from dotenv import load_dotenv
import os

load_dotenv()


def get_auth_token() -> str:
    service_secret = os.environ.get("SERVICE_SECRET")
    license_key = os.environ.get("LICENSE_KEY")

    text = f"{service_secret}:{license_key}"

    return base64.b64encode(text.encode("utf-8")).decode("utf-8")
