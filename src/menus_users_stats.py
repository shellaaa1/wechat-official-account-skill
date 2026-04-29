from __future__ import annotations

from typing import Any

from .client import WechatClient


def create_menu(menu: dict[str, Any]) -> dict[str, Any]:
    return WechatClient().post("menu/create", menu)


def get_menu() -> dict[str, Any]:
    return WechatClient().get("menu/get")


def delete_menu() -> dict[str, Any]:
    return WechatClient().get("menu/delete")


def list_users(next_openid: str | None = None) -> dict[str, Any]:
    params = {"next_openid": next_openid} if next_openid else {}
    return WechatClient().get("user/get", params=params)


def get_user_info(openid: str, lang: str = "zh_CN") -> dict[str, Any]:
    return WechatClient().get("user/info", params={"openid": openid, "lang": lang})


def set_user_remark(openid: str, remark: str) -> dict[str, Any]:
    return WechatClient().post("user/info/updateremark", {"openid": openid, "remark": remark})


def get_article_stats(begin: str, end: str) -> dict[str, Any]:
    return WechatClient().post("datacube/getarticletotal", {"begin_date": begin, "end_date": end})
