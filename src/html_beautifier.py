from __future__ import annotations

from pathlib import Path
from typing import Any

import mistune
import yaml
from bs4 import BeautifulSoup, Tag

from .auth import load_config


ROOT_DIR = Path(__file__).resolve().parents[1]
THEME_DIR = ROOT_DIR / "themes"


DEFAULT_THEME: dict[str, Any] = {
    "base": {
        "font_family": "'PingFang SC', 'Microsoft YaHei', sans-serif",
        "font_size": "16px",
        "color": "#333333",
        "line_height": "1.8",
    },
    "h1": {"font_size": "24px", "font_weight": "700", "margin": "24px 0 16px"},
    "h2": {"font_size": "21px", "font_weight": "700", "margin": "24px 0 12px", "border_left": "4px solid #576b95", "padding_left": "10px"},
    "h3": {"font_size": "18px", "font_weight": "700", "margin": "20px 0 10px"},
    "p": {"margin": "0 0 16px"},
    "blockquote": {"border_left": "4px solid #d0d7de", "padding": "8px 12px", "color": "#57606a", "background": "#f6f8fa"},
    "ul": {"padding_left": "22px", "margin": "0 0 16px"},
    "ol": {"padding_left": "22px", "margin": "0 0 16px"},
    "li": {"margin": "6px 0"},
    "strong": {"font_weight": "700"},
    "code": {"background": "#f6f8fa", "padding": "2px 4px", "border_radius": "4px"},
    "pre": {"background": "#f6f8fa", "padding": "12px", "overflow": "auto", "border_radius": "6px"},
    "img": {"max_width": "100%", "height": "auto", "margin": "16px 0"},
    "a": {"color": "#576b95"},
}

STYLE_KEY_MAP = {
    "font_family": "font-family",
    "font_size": "font-size",
    "font_weight": "font-weight",
    "line_height": "line-height",
    "border_left": "border-left",
    "padding_left": "padding-left",
    "margin_bottom": "margin-bottom",
    "max_width": "max-width",
    "border_radius": "border-radius",
    "box_shadow": "box-shadow",
}


def load_theme(theme_name: str | None = None) -> dict[str, Any]:
    name = theme_name or load_config().get("theme") or "default"
    path = THEME_DIR / f"{name}.yaml"
    theme = DEFAULT_THEME.copy()
    if path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(loaded, dict):
            for key, value in loaded.items():
                if isinstance(value, dict) and isinstance(theme.get(key), dict):
                    merged = dict(theme[key])
                    merged.update(value)
                    theme[key] = merged
                else:
                    theme[key] = value
    return theme


def style_dict_to_text(style: dict[str, Any]) -> str:
    pairs = []
    for key, value in style.items():
        if value is None:
            continue
        css_key = STYLE_KEY_MAP.get(key, key.replace("_", "-"))
        pairs.append(f"{css_key}: {value}")
    return "; ".join(pairs)


def flatten_lists(soup: BeautifulSoup) -> None:
    for list_node in list(soup.find_all(["ul", "ol"])):
        if not isinstance(list_node, Tag):
            continue
        ordered = list_node.name == "ol"
        replacement_nodes = []
        index = 1
        for child in list(list_node.children):
            if not isinstance(child, Tag) or child.name != "li":
                continue
            marker = f"{index}." if ordered else "•"
            paragraph = soup.new_tag("p")
            paragraph["data-list-item"] = "true"
            paragraph["style"] = "margin: 0 0 8px; padding-left: 1.2em; text-indent: -1.2em"
            paragraph.append(f"{marker} ")
            for item_child in list(child.contents):
                paragraph.append(item_child.extract())
            replacement_nodes.append(paragraph)
            index += 1
        for node in reversed(replacement_nodes):
            list_node.insert_after(node)
        list_node.decompose()


def apply_inline_styles(html: str, theme: dict[str, Any]) -> str:
    soup = BeautifulSoup(html, "html5lib")
    body = soup.body or soup
    flatten_lists(soup)
    for element in body.find_all(True):
        if not isinstance(element, Tag):
            continue
        tag_style = {}
        if element.get("data-list-item") == "true":
            element.attrs.pop("data-list-item", None)
        elif element.name in {"p", "h1", "h2", "h3", "h4", "blockquote", "ul", "ol", "li", "pre", "code", "img", "a", "strong"}:
            tag_style.update(theme.get(element.name, {}))
        if tag_style:
            existing = element.get("style", "")
            inline = style_dict_to_text(tag_style)
            element["style"] = f"{existing}; {inline}".strip("; ").strip()
    wrapper_style = style_dict_to_text(theme.get("base", {}))
    content = "".join(str(child) for child in body.children)
    return f'<section style="{wrapper_style}">{content}</section>'


def add_footer(html: str) -> str:
    footer = (
        '<section style="margin-top: 28px; padding-top: 16px; border-top: 1px solid #eeeeee; '
        'font-size: 13px; color: #888888; text-align: center;">本文由 AI 助手生成并排版</section>'
    )
    return html + footer


def markdown_to_wechat_html(markdown_text: str, theme_name: str | None = None, footer: bool | None = None) -> str:
    markdown = mistune.create_markdown(escape=False, plugins=["strikethrough", "table", "url"])
    html = markdown(markdown_text)
    themed = apply_inline_styles(html, load_theme(theme_name))
    if footer is None:
        footer = load_config().get("footer_signature", "true") != "false"
    return add_footer(themed) if footer else themed
