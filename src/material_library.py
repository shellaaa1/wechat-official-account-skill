from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from .auth import ROOT_DIR


ASSET_ROOT = ROOT_DIR / "assets" / "library"
INDEX_FILE = ASSET_ROOT / "index.yaml"


DEFAULT_MATERIAL_SLOTS = {
    "cover": "covers/default_cover.png",
    "banner": "banners/default_banner.png",
    "hero": "illustrations/default_hero.png",
    "icon": "icons/default_icon.png",
    "divider": "dividers/default_divider.png",
    "background": "backgrounds/default_background.png",
}


def load_asset_index() -> dict[str, Any]:
    if not INDEX_FILE.exists():
        return {"assets": []}
    data = yaml.safe_load(INDEX_FILE.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {"assets": []}


def resolve_asset_path(relative_path: str) -> Path:
    return (ASSET_ROOT / relative_path).resolve()


def _score_asset(asset: dict[str, Any], template_meta: dict[str, Any], slot: str) -> int:
    score = 0
    if asset.get("slot") == slot:
        score += 20
    template_id = str(template_meta.get("id", ""))
    category = str(template_meta.get("category", ""))
    theme = str(template_meta.get("theme", ""))
    style = str(template_meta.get("style", ""))
    tags = {str(tag) for tag in asset.get("tags", [])}
    if template_id and template_id in tags:
        score += 10
    if category and category in tags:
        score += 8
    if theme and theme in tags:
        score += 6
    if style and style in tags:
        score += 6
    return score


def select_asset(slot: str, template_meta: dict[str, Any]) -> str:
    assets = load_asset_index().get("assets", [])
    candidates = [asset for asset in assets if isinstance(asset, dict) and asset.get("slot") == slot]
    if not candidates:
        return str(resolve_asset_path(DEFAULT_MATERIAL_SLOTS.get(slot, "icons/default_icon.png")))
    ranked = sorted(candidates, key=lambda asset: _score_asset(asset, template_meta, slot), reverse=True)
    best_score = _score_asset(ranked[0], template_meta, slot)
    tied = [asset for asset in ranked if _score_asset(asset, template_meta, slot) == best_score]
    seed = f"{template_meta.get('id', '')}:{template_meta.get('name', '')}:{slot}".encode("utf-8")
    selected = tied[int(hashlib.sha256(seed).hexdigest(), 16) % len(tied)]
    return str(resolve_asset_path(str(selected.get("path"))))


def select_materials(template_meta: dict[str, Any]) -> dict[str, str]:
    slots = template_meta.get("materials") or list(DEFAULT_MATERIAL_SLOTS.keys())
    if isinstance(slots, dict):
        slots = list(slots.keys())
    if not isinstance(slots, list):
        slots = list(DEFAULT_MATERIAL_SLOTS.keys())
    result = {}
    for slot in slots:
        if isinstance(slot, str):
            result[f"material_{slot}"] = select_asset(slot, template_meta)
    return result
