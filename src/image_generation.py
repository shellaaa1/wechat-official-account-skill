from __future__ import annotations

import base64
import json
import mimetypes
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from .auth import ROOT_DIR, ConfigError, load_config
from .material import upload_image


DEFAULT_OUTPUT_DIR = ROOT_DIR / "generated_images"
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.M)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")


class ImageGenerationError(RuntimeError):
    pass


def require_image_config() -> dict[str, str]:
    config = load_config()
    if not config.get("image_api_key"):
        raise ConfigError("请先在 .env 中配置 IMAGE_API_KEY")
    return config


def _guess_suffix(content_type: str | None, fallback: str = ".png") -> str:
    if content_type:
        suffix = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
        if suffix:
            return ".jpg" if suffix == ".jpe" else suffix
    return fallback


def _write_base64_image(value: str, output_path: Path) -> Path:
    if "," in value and value.strip().startswith("data:"):
        value = value.split(",", 1)[1]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(value))
    return output_path


def _download_image(url: str, output_path: Path) -> Path:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    suffix = _guess_suffix(response.headers.get("Content-Type"), output_path.suffix or ".png")
    if not output_path.suffix:
        output_path = output_path.with_suffix(suffix)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)
    return output_path


def _build_output_path(output_dir: Path, filename: str | None, index: int, suffix: str = ".png") -> Path:
    if filename:
        path = output_dir / filename
        if index > 0:
            path = path.with_name(f"{path.stem}_{index + 1}{path.suffix or suffix}")
        if not path.suffix:
            path = path.with_suffix(suffix)
        return path
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return output_dir / f"image_{timestamp}_{index + 1}{suffix}"


def generate_images(
    prompt: str,
    output_dir: str | Path | None = None,
    filename: str | None = None,
    model: str | None = None,
    size: str | None = None,
    n: int = 1,
    response_format: str | None = None,
) -> list[Path]:
    config = require_image_config()
    api_base_url = config.get("image_api_base_url") or "https://api.openai.com/v1"
    endpoint = config.get("image_api_endpoint") or "/images/generations"
    url = api_base_url.rstrip("/") + "/" + endpoint.lstrip("/")
    output_path = Path(output_dir).expanduser().resolve() if output_dir else DEFAULT_OUTPUT_DIR

    payload: dict[str, Any] = {
        "model": model or config.get("image_model") or "gpt-image-1",
        "prompt": prompt,
        "size": size or config.get("image_size") or "1024x1024",
        "n": n,
    }
    fmt = response_format or config.get("image_response_format")
    if fmt:
        payload["response_format"] = fmt
    extra_json = config.get("image_api_extra_json")
    if extra_json:
        try:
            extra = json.loads(extra_json)
        except json.JSONDecodeError as exc:
            raise ImageGenerationError("IMAGE_API_EXTRA_JSON 不是合法 JSON") from exc
        if isinstance(extra, dict):
            payload.update(extra)

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {config['image_api_key']}",
            "Content-Type": "application/json; charset=utf-8",
        },
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=180,
    )
    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise ImageGenerationError(f"图片生成接口返回非 JSON：HTTP {response.status_code}") from exc
    if response.status_code >= 400:
        message = data.get("error", data)
        raise ImageGenerationError(f"图片生成失败：HTTP {response.status_code} {message}")

    images = data.get("data")
    if not isinstance(images, list) or not images:
        raise ImageGenerationError(f"图片生成接口未返回 data 列表：{data}")

    saved: list[Path] = []
    for index, item in enumerate(images):
        if not isinstance(item, dict):
            continue
        if item.get("b64_json"):
            path = _build_output_path(output_path, filename, index, ".png")
            saved.append(_write_base64_image(str(item["b64_json"]), path))
            continue
        if item.get("url"):
            parsed = urlparse(str(item["url"]))
            suffix = Path(parsed.path).suffix or ".png"
            path = _build_output_path(output_path, filename, index, suffix)
            saved.append(_download_image(str(item["url"]), path))
    if not saved:
        raise ImageGenerationError(f"图片生成接口返回数据中没有 url 或 b64_json：{data}")
    return saved


def generate_and_upload(
    prompt: str,
    output_dir: str | Path | None = None,
    filename: str | None = None,
    model: str | None = None,
    size: str | None = None,
    n: int = 1,
    response_format: str | None = None,
) -> list[dict[str, Any]]:
    paths = generate_images(
        prompt=prompt,
        output_dir=output_dir,
        filename=filename,
        model=model,
        size=size,
        n=n,
        response_format=response_format,
    )
    result = []
    for path in paths:
        uploaded = upload_image(str(path))
        uploaded["local_path"] = str(path)
        result.append(uploaded)
    return result


def extract_illustration_slots(markdown_text: str, max_images: int = 3) -> list[dict[str, str]]:
    matches = list(HEADING_RE.finditer(markdown_text))
    slots: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        level, title = match.group(1), match.group(2).strip()
        if len(level) == 1 and index == 0:
            continue
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(markdown_text)
        section = markdown_text[match.end():next_start].strip()
        if not section or IMAGE_RE.search(section):
            continue
        summary = re.sub(r"[`*_>#\-\[\]()]+", "", section)
        summary = re.sub(r"\s+", " ", summary).strip()[:260]
        slots.append({"title": title, "summary": summary})
        if len(slots) >= max_images:
            break
    if slots:
        return slots

    plain = re.sub(r"[`*_>#\-\[\]()]+", "", markdown_text)
    plain = re.sub(r"\s+", " ", plain).strip()[:260]
    return [{"title": "文章配图", "summary": plain}] if plain and max_images > 0 else []


def build_illustration_prompt(title: str, summary: str, style: str) -> str:
    return (
        f"为微信公众号文章段落《{title}》生成一张正文插图。"
        f"段落内容：{summary}。"
        f"视觉要求：{style}。"
        "不要出现水印、二维码、品牌 Logo、乱码文字；画面适合公众号正文阅读，构图清晰，留白舒适。"
    )


def insert_illustrations(markdown_text: str, illustrations: list[dict[str, str]]) -> str:
    result = markdown_text
    for item in illustrations:
        title = re.escape(item["title"])
        image_markdown = f"\n\n![{item['alt']}]({item['src']})\n"
        pattern = re.compile(rf"^(##+\s+{title}\s*)$", re.M)
        match = pattern.search(result)
        if match:
            insert_at = match.end()
            result = result[:insert_at] + image_markdown + result[insert_at:]
        else:
            result += image_markdown
    return result


def illustrate_article(
    article_file: str | Path,
    output_file: str | Path | None = None,
    output_dir: str | Path | None = None,
    max_images: int = 3,
    style: str = "现代科技感扁平插画，16:9，公众号正文配图",
    upload: bool = False,
    model: str | None = None,
    size: str | None = None,
    response_format: str | None = None,
) -> dict[str, Any]:
    source_path = Path(article_file).expanduser().resolve()
    markdown_text = source_path.read_text(encoding="utf-8")
    image_dir = Path(output_dir).expanduser().resolve() if output_dir else source_path.parent / f"{source_path.stem}_images"
    slots = extract_illustration_slots(markdown_text, max_images=max_images)
    illustrations: list[dict[str, str]] = []

    for index, slot in enumerate(slots):
        prompt = build_illustration_prompt(slot["title"], slot["summary"], style)
        filename = f"{source_path.stem}_illustration_{index + 1}.png"
        paths = generate_images(
            prompt=prompt,
            output_dir=image_dir,
            filename=filename,
            model=model,
            size=size,
            n=1,
            response_format=response_format,
        )
        local_path = paths[0]
        src = str(local_path)
        media_id = ""
        if upload:
            uploaded = upload_image(str(local_path))
            media_id = str(uploaded.get("media_id", ""))
            src = str(uploaded.get("url") or uploaded.get("media_id") or local_path)
        illustrations.append(
            {
                "title": slot["title"],
                "alt": f"{slot['title']} 插图",
                "src": src,
                "local_path": str(local_path),
                "media_id": media_id,
                "prompt": prompt,
            }
        )

    output_path = Path(output_file).expanduser().resolve() if output_file else source_path.with_name(f"{source_path.stem}_illustrated.md")
    output_path.write_text(insert_illustrations(markdown_text, illustrations), encoding="utf-8")
    return {"output_file": str(output_path), "illustrations": illustrations}
