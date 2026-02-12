#!/usr/bin/env python3
"""List skills from a GitHub repo path and compare metadata.version."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import json
import os
import re
import sys
import urllib.error

from github_utils import (
    DEFAULT_REF,
    DEFAULT_REPO,
    DEFAULT_SKILLS_PATH,
    github_api_contents_url,
    github_request,
    resolve_skills_dir,
)

DEFAULT_PATH = DEFAULT_SKILLS_PATH


class ListError(Exception):
    pass


class Args(argparse.Namespace):
    repo: str
    path: str
    ref: str
    format: str


@dataclass
class RemoteSkill:
    name: str
    version: str | None


@dataclass
class SkillStatus:
    name: str
    remote_version: str | None
    local_version: str | None
    installed: bool
    status: str
    reason: str | None


def _request(url: str) -> bytes:
    return github_request(url, "sophnet-skill-list")


def _skills_root() -> str:
    return resolve_skills_dir()


def _installed(skill_name: str) -> bool:
    return os.path.isdir(os.path.join(_skills_root(), skill_name))


def _fetch_json(url: str) -> object:
    payload = _request(url)
    return json.loads(payload.decode("utf-8"))


def _fetch_remote_skill_names(repo: str, path: str, ref: str) -> list[str]:
    api_url = github_api_contents_url(repo, path, ref)
    try:
        data = _fetch_json(api_url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise ListError(
                "Skills path not found: "
                f"https://github.com/{repo}/tree/{ref}/{path}"
            ) from exc
        raise ListError(f"Failed to fetch skills: HTTP {exc.code}") from exc
    except json.JSONDecodeError as exc:
        raise ListError(f"Failed to parse skills list: {exc}") from exc

    if not isinstance(data, list):
        raise ListError("Unexpected skills listing response.")
    skills = [item["name"] for item in data if item.get("type") == "dir"]
    return sorted(skills)


def _decode_github_content(data: dict[str, object]) -> str | None:
    content = data.get("content")
    encoding = data.get("encoding")
    if not isinstance(content, str):
        return None
    if encoding == "base64":
        try:
            return base64.b64decode(content.encode("utf-8")).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return None
    return content


def _extract_frontmatter(text: str) -> str | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if match:
        return match.group(1)
    return None


def _extract_metadata_version(frontmatter: str) -> str | None:
    meta_match = re.search(
        r"(?ms)^metadata:\s*\n(?P<body>(?:[ \t].*\n?)*)", frontmatter
    )
    if not meta_match:
        return None
    body = meta_match.group("body")
    version_match = re.search(
        r"(?m)^[ \t]*version:\s*[\"']?([0-9A-Za-z._-]+)[\"']?\s*$",
        body,
    )
    if not version_match:
        return None
    return version_match.group(1)


def _version_from_skill_md(text: str) -> str | None:
    frontmatter = _extract_frontmatter(text)
    if not frontmatter:
        return None
    return _extract_metadata_version(frontmatter)


def _read_remote_version(repo: str, path: str, ref: str, skill_name: str) -> str | None:
    skill_md_path = f"{path.strip('/')}/{skill_name}/SKILL.md".strip("/")
    api_url = github_api_contents_url(repo, skill_md_path, ref)
    try:
        data = _fetch_json(api_url)
    except (urllib.error.HTTPError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    text = _decode_github_content(data)
    if text is None:
        return None
    return _version_from_skill_md(text)


def _read_local_version(skill_name: str) -> str | None:
    skill_md = os.path.join(_skills_root(), skill_name, "SKILL.md")
    if not os.path.isfile(skill_md):
        return None
    try:
        with open(skill_md, "r", encoding="utf-8") as file_handle:
            text = file_handle.read()
    except OSError:
        return None
    return _version_from_skill_md(text)


def _version_tokens(version: str) -> list[int | str]:
    tokens: list[int | str] = []
    for chunk in re.split(r"[._-]+", version):
        if not chunk:
            continue
        if chunk.isdigit():
            tokens.append(int(chunk))
        else:
            tokens.append(chunk.lower())
    return tokens


def _compare_versions(left: str, right: str) -> int:
    left_tokens = _version_tokens(left)
    right_tokens = _version_tokens(right)
    max_len = max(len(left_tokens), len(right_tokens))
    for idx in range(max_len):
        left_token: int | str = left_tokens[idx] if idx < len(left_tokens) else 0
        right_token: int | str = right_tokens[idx] if idx < len(right_tokens) else 0
        if left_token == right_token:
            continue
        if isinstance(left_token, int) and isinstance(right_token, int):
            return -1 if left_token < right_token else 1
        left_str = str(left_token)
        right_str = str(right_token)
        if left_str < right_str:
            return -1
        return 1
    return 0


def _classify_skill(remote_skill: RemoteSkill) -> SkillStatus:
    if not _installed(remote_skill.name):
        return SkillStatus(
            name=remote_skill.name,
            remote_version=remote_skill.version,
            local_version=None,
            installed=False,
            status="not_installed",
            reason=None,
        )

    local_version = _read_local_version(remote_skill.name)
    if not remote_skill.version:
        return SkillStatus(
            name=remote_skill.name,
            remote_version=None,
            local_version=local_version,
            installed=True,
            status="needs_update",
            reason="remote metadata.version missing",
        )
    if not local_version:
        return SkillStatus(
            name=remote_skill.name,
            remote_version=remote_skill.version,
            local_version=None,
            installed=True,
            status="needs_update",
            reason="local metadata.version missing",
        )

    if _compare_versions(local_version, remote_skill.version) < 0:
        return SkillStatus(
            name=remote_skill.name,
            remote_version=remote_skill.version,
            local_version=local_version,
            installed=True,
            status="needs_update",
            reason=f"v{local_version} -> v{remote_skill.version}",
        )

    return SkillStatus(
        name=remote_skill.name,
        remote_version=remote_skill.version,
        local_version=local_version,
        installed=True,
        status="latest",
        reason=None,
    )


def _section(title: str, names: list[str]) -> str:
    lines = [f"{title}:"]
    if names:
        for name in names:
            lines.append(f"- {name}")
    else:
        lines.append("- (none)")
    return "\n".join(lines)


def _status_label(skill: SkillStatus) -> str:
    if skill.status == "not_installed":
        if skill.remote_version:
            return f"not installed, remote v{skill.remote_version}"
        return "not installed"
    if skill.status == "needs_update":
        if skill.reason:
            return f"needs update: {skill.reason}"
        return "needs update"
    if skill.remote_version:
        return f"latest version: v{skill.remote_version}"
    return "latest version"


def _emit_text(repo: str, path: str, ref: str, statuses: list[SkillStatus]) -> None:
    location = f"https://github.com/{repo}/tree/{ref}/{path.strip('/') or ''}".rstrip("/")
    print(f"Skills from {location}:")
    for idx, skill in enumerate(statuses, start=1):
        print(f"{idx}. {skill.name} [{_status_label(skill)}]")
    print()

    not_installed = [skill.name for skill in statuses if skill.status == "not_installed"]
    needs_update = [skill.name for skill in statuses if skill.status == "needs_update"]
    latest = [skill.name for skill in statuses if skill.status == "latest"]
    print(_section("Not installed", not_installed))
    print()
    print(_section("Need update", needs_update))
    print()
    print(_section("Latest version", latest))
    print()
    _emit_guidance(repo, path, statuses)


def _install_paths(path: str, names: list[str]) -> list[str]:
    normalized = path.strip("/")
    return [f"{normalized}/{name}" if normalized else name for name in names]


def _emit_guidance(repo: str, path: str, statuses: list[SkillStatus]) -> None:
    pending_names = [
        skill.name
        for skill in statuses
        if skill.status in ("not_installed", "needs_update")
    ]
    pending_paths = _install_paths(path, pending_names)
    base_path = path.strip("/") or "<path>"
    print("Next step:")
    if pending_paths:
        joined_paths = " ".join(pending_paths)
        print("1. Install all pending skills:")
        print(
            f"   python3 scripts/install-skill-from-github.py --repo {repo} "
            f"--path {joined_paths} --replace"
        )
        print("2. Install specific skills (replace selected ones if already installed):")
        print(
            "   python3 scripts/install-skill-from-github.py --repo "
            f"{repo} --path {base_path}/<skill-1> {base_path}/<skill-2> --replace"
        )
        print("Would you like to install all pending skills, or only specific ones?")
    else:
        print("- All listed skills are at the latest version.")
        print("- If you still want to reinstall one skill, run:")
        print(
            "  python3 scripts/install-skill-from-github.py --repo "
            f"{repo} --path {base_path}/<skill-name> --replace"
        )


def _parse_args(argv: list[str]) -> Args:
    parser = argparse.ArgumentParser(description="List skills.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument(
        "--path",
        default=DEFAULT_PATH,
        help=f"Repo path to list (default: {DEFAULT_PATH})",
    )
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        names = _fetch_remote_skill_names(args.repo, args.path, args.ref)
        remote_skills = [
            RemoteSkill(
                name=name,
                version=_read_remote_version(args.repo, args.path, args.ref, name),
            )
            for name in names
        ]
        statuses = [_classify_skill(skill) for skill in remote_skills]

        if args.format == "json":
            payload = [
                {
                    "name": skill.name,
                    "installed": skill.installed,
                    "status": skill.status,
                    "reason": skill.reason,
                    "local_version": skill.local_version,
                    "remote_version": skill.remote_version,
                }
                for skill in statuses
            ]
            print(json.dumps(payload))
        else:
            _emit_text(args.repo, args.path, args.ref, statuses)
        return 0
    except ListError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
