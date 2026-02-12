#!/usr/bin/env python3
"""Install/update pending Sophnet skills, then run their local install scripts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

from github_utils import DEFAULT_REF, DEFAULT_REPO, DEFAULT_SKILLS_PATH, resolve_skills_dir


def _skills_root() -> str:
    return resolve_skills_dir()


def _script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _run(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def _install_paths(path: str, names: list[str]) -> list[str]:
    normalized = path.strip("/")
    return [f"{normalized}/{name}" if normalized else name for name in names]


def _pending_skills(repo: str, path: str, ref: str) -> list[str]:
    list_script = os.path.join(_script_dir(), "list-skills.py")
    result = _run(["python3", list_script, "--repo", repo, "--path", path, "--ref", ref, "--format", "json"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "list-skills failed")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid list-skills JSON output: {exc}") from exc
    if not isinstance(payload, list):
        raise RuntimeError("list-skills returned unexpected payload")
    pending: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        status = str(item.get("status", "")).strip()
        if name and status in {"not_installed", "needs_update"}:
            pending.append(name)
    return pending


def _run_skill_install_script(skill_name: str) -> tuple[bool, str]:
    skill_dir = os.path.join(_skills_root(), skill_name)
    candidates = [
        (["bash", "scripts/install.sh"], os.path.join(skill_dir, "scripts", "install.sh")),
        (["python3", "scripts/install.py"], os.path.join(skill_dir, "scripts", "install.py")),
        (["bash", "install.sh"], os.path.join(skill_dir, "install.sh")),
        (["python3", "install.py"], os.path.join(skill_dir, "install.py")),
    ]
    for command, candidate in candidates:
        if not os.path.isfile(candidate):
            continue
        result = _run(command, cwd=skill_dir)
        combined = "\n".join([result.stdout.strip(), result.stderr.strip()]).strip()
        if result.returncode == 0:
            return True, combined or f"ran {' '.join(command)}"
        return False, combined or f"{' '.join(command)} failed with exit {result.returncode}"
    return True, "no install script found"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install all pending Sophnet skills.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--path", default=DEFAULT_SKILLS_PATH)
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument("--replace", action="store_true", default=True)
    parser.add_argument("--no-replace", action="store_false", dest="replace")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        pending = _pending_skills(args.repo, args.path, args.ref)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not pending:
        print("All skills are already at the latest version.")
        return 0

    install_script = os.path.join(_script_dir(), "install-skill-from-github.py")
    install_paths = _install_paths(args.path, pending)
    command = ["python3", install_script, "--repo", args.repo, "--ref", args.ref, "--path", *install_paths]
    if args.replace:
        command.append("--replace")
    install_result = _run(command, cwd=_script_dir())
    if install_result.stdout.strip():
        print(install_result.stdout.strip())
    if install_result.returncode != 0:
        print(install_result.stderr.strip() or "install-skill-from-github.py failed", file=sys.stderr)
        return install_result.returncode

    failures: list[str] = []
    for skill_name in pending:
        ok, detail = _run_skill_install_script(skill_name)
        if ok:
            print(f"[{skill_name}] {detail}")
            continue
        failures.append(f"[{skill_name}] {detail}")

    if failures:
        print("Install scripts failed:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("🎉 恭喜！Sophnet Skills 现在已经可用了，快去体验一下吧！🚀")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
