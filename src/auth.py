from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
CACHE_FILE = ROOT_DIR / ".token_cache.json"


class ConfigError(RuntimeError):
    pass


def load_config() -> dict[str, str]:
    load_dotenv(ROOT_DIR / ".env")
    config = {
        "app_id": os.getenv("WECHAT_APP_ID", "").strip(),
        "app_secret": os.getenv("WECHAT_APP_SECRET", "").strip(),
        "token": os.getenv("WECHAT_TOKEN", "").strip(),
        "aes_key": os.getenv("WECHAT_AES_KEY", "").strip(),
        "theme": os.getenv("THEME", "default").strip() or "default",
        "footer_signature": os.getenv("FOOTER_SIGNATURE", "true").strip().lower(),
        "image_api_base_url": os.getenv("IMAGE_API_BASE_URL", "https://api.openai.com/v1").strip(),
        "image_api_endpoint": os.getenv("IMAGE_API_ENDPOINT", "/images/generations").strip(),
        "image_api_key": os.getenv("IMAGE_API_KEY", "").strip(),
        "image_model": os.getenv("IMAGE_MODEL", "gpt-image-1").strip(),
        "image_size": os.getenv("IMAGE_SIZE", "1024x1024").strip(),
        "image_response_format": os.getenv("IMAGE_RESPONSE_FORMAT", "").strip(),
        "image_api_extra_json": os.getenv("IMAGE_API_EXTRA_JSON", "").strip(),
    }
    return config


def require_credentials() -> dict[str, str]:
    config = load_config()
    if not config["app_id"] or not config["app_secret"]:
        raise ConfigError("请先在 .env 中配置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
    return config


def read_cached_token() -> str | None:
    if not CACHE_FILE.exists():
        return None
    try:
        data: dict[str, Any] = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if int(data.get("expires_at", 0)) <= int(time.time()) + 60:
        return None
    token = data.get("access_token")
    return token if isinstance(token, str) and token else None


def write_cached_token(access_token: str, expires_in: int) -> None:
    data = {
        "access_token": access_token,
        "expires_at": int(time.time()) + max(expires_in - 120, 60),
    }
    CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
