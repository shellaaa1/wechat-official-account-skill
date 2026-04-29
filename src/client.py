from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from .auth import read_cached_token, require_credentials, write_cached_token


API_BASE = "https://api.weixin.qq.com/cgi-bin"


class WechatAPIError(RuntimeError):
    pass


class WechatClient:
    def __init__(self) -> None:
        self.config = require_credentials()

    def get_access_token(self) -> str:
        cached = read_cached_token()
        if cached:
            return cached
        response = requests.get(
            f"{API_BASE}/token",
            params={
                "grant_type": "client_credential",
                "appid": self.config["app_id"],
                "secret": self.config["app_secret"],
            },
            timeout=30,
        )
        data = self._parse_response(response)
        access_token = data.get("access_token")
        if not access_token:
            raise WechatAPIError(f"获取 access_token 失败：{data}")
        write_cached_token(str(access_token), int(data.get("expires_in", 7200)))
        return str(access_token)

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = dict(params or {})
        params["access_token"] = self.get_access_token()
        response = requests.get(f"{API_BASE}/{path.lstrip('/')}", params=params, timeout=30)
        return self._parse_response(response)

    def post(self, path: str, payload: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = dict(params or {})
        params["access_token"] = self.get_access_token()
        body = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
        response = requests.post(
            f"{API_BASE}/{path.lstrip('/')}",
            params=params,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=30,
        )
        return self._parse_response(response)

    def post_file(self, path: str, file_path: Path, field_name: str = "media", params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = dict(params or {})
        params["access_token"] = self.get_access_token()
        with file_path.open("rb") as file_obj:
            response = requests.post(
                f"{API_BASE}/{path.lstrip('/')}",
                params=params,
                files={field_name: (file_path.name, file_obj)},
                timeout=60,
            )
        return self._parse_response(response)

    @staticmethod
    def _parse_response(response: requests.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise WechatAPIError(f"微信 API 返回非 JSON 响应：HTTP {response.status_code}") from exc
        errcode = data.get("errcode")
        if errcode not in (None, 0):
            raise WechatAPIError(f"微信 API 错误 {errcode}: {data.get('errmsg', data)}")
        return data
