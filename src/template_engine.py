from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .material_library import select_materials


ROOT_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT_DIR / "templates"
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)
VARIABLE_RE = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


class TemplateError(RuntimeError):
    pass


def _read_template(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {"name": path.stem, "category": "未分类", "variables": []}, text
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        raise TemplateError(f"模板 YAML 头格式错误：{path.name}")
    return meta, match.group(2)


def list_templates() -> list[dict[str, Any]]:
    templates: list[dict[str, Any]] = []
    for path in sorted(TEMPLATE_DIR.glob("*.md")):
        meta, _ = _read_template(path)
        templates.append(
            {
                "id": path.stem,
                "name": meta.get("name", path.stem),
                "category": meta.get("category", "未分类"),
                "theme": meta.get("theme"),
                "style": meta.get("style"),
                "materials": meta.get("materials", []),
                "variables": meta.get("variables", []),
            }
        )
    return templates


def find_template(name: str) -> Path:
    candidates = [TEMPLATE_DIR / f"{name}.md"]
    for path in TEMPLATE_DIR.glob("*.md"):
        try:
            meta, _ = _read_template(path)
        except TemplateError:
            continue
        if meta.get("name") == name:
            candidates.append(path)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise TemplateError(f"模板不存在：{name}")


def show_template(name: str) -> dict[str, Any]:
    path = find_template(name)
    meta, body = _read_template(path)
    return {
        "id": path.stem,
        "name": meta.get("name", path.stem),
        "category": meta.get("category", "未分类"),
        "theme": meta.get("theme"),
        "style": meta.get("style"),
        "materials": meta.get("materials", []),
        "variables": meta.get("variables", []),
        "body": body,
    }


def render_template(name: str, variables: dict[str, str]) -> str:
    template = show_template(name)
    values: dict[str, str] = {}
    values.update(select_materials(template))
    for variable in template.get("variables", []):
        if isinstance(variable, dict) and variable.get("name"):
            key = str(variable["name"])
            values[key] = str(variable.get("default", ""))
    values.update(variables)

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))

    return VARIABLE_RE.sub(replace, template["body"])
