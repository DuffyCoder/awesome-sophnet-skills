#!/usr/bin/env python3
"""Shared GitHub helpers for skill install scripts."""

from __future__ import annotations

import os
import urllib.request

DEFAULT_REPO = "DuffyCoder/awesome-sophnet-skills"
DEFAULT_SKILLS_PATH = "skills"
DEFAULT_REF = "main"


def github_request(url: str, user_agent: str) -> bytes:
    headers = {"User-Agent": user_agent}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def github_api_contents_url(repo: str, path: str, ref: str) -> str:
    normalized_path = path.strip("/")
    if normalized_path:
        return f"https://api.github.com/repos/{repo}/contents/{normalized_path}?ref={ref}"
    return f"https://api.github.com/repos/{repo}/contents?ref={ref}"
