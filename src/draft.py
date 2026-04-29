from __future__ import annotations

from pathlib import Path
from typing import Any

from .client import WechatClient
from .html_beautifier import markdown_to_wechat_html


def create_draft(
    title: str,
    content_file: str | None,
    cover_media_id: str,
    author: str = "",
    digest: str = "",
    content: str | None = None,
    allow_comment: bool = True,
    need_open_comment: bool = False,
) -> dict[str, Any]:
    if content_file:
        source_path = Path(content_file).expanduser().resolve()
        source = source_path.read_text(encoding="utf-8")
        if source_path.suffix.lower() in {".html", ".htm"}:
            html = source
        else:
            html = markdown_to_wechat_html(source)
    elif content:
        html = content
    else:
        raise ValueError("必须提供 content_file 或 content")

    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": html,
        "thumb_media_id": cover_media_id,
        "need_open_comment": 1 if need_open_comment else 0,
        "only_fans_can_comment": 0 if allow_comment else 1,
    }
    return WechatClient().post("draft/add", {"articles": [article]})


def list_drafts(offset: int = 0, count: int = 20, no_content: bool = True) -> dict[str, Any]:
    return WechatClient().post(
        "draft/batchget",
        {"offset": offset, "count": count, "no_content": 1 if no_content else 0},
    )


def delete_draft(media_id: str) -> dict[str, Any]:
    return WechatClient().post("draft/delete", {"media_id": media_id})


def publish_draft(media_id: str) -> dict[str, Any]:
    return WechatClient().post("freepublish/submit", {"media_id": media_id})
