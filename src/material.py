from __future__ import annotations

from pathlib import Path
from typing import Any

from .client import WechatClient


ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif"}


def upload_image(file_path: str) -> dict[str, Any]:
    path = Path(file_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"图片文件不存在：{path}")
    if path.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
        raise ValueError("仅支持 jpg、png、gif 图片")
    client = WechatClient()
    return client.post_file("material/add_material", path, params={"type": "image"})
