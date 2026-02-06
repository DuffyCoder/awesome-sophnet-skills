---
name: sophnet-skill-installer
description: Use when a user asks to list or install Sophnet skills. First install from DuffyCoder/awesome-sophnet-skills, and if a skill is not found there, install from another GitHub repo/path.
metadata:
  short-description: Install and compare Sophnet skills by metadata.version
---

# Sophnet Skill Installer

## Overview
Install skills into `$SOPHNET_HOME/skills` with this priority:
1. Default source: `https://github.com/DuffyCoder/awesome-sophnet-skills` under `skills/`.
2. Fallback source: another user-provided GitHub repo/path when the skill is not found in the default source.
Compare installed versions using each skill's `SKILL.md` YAML frontmatter:
`metadata.version`.

## Workflow
1. On every trigger of this skill, first run `list-skills.py` and show:
   all skills in the default repo, then grouped sections: `Not installed`, `Need update`, `Latest version`.
2. For version comparison, read `metadata.version` from:
   remote `skills/<skill-name>/SKILL.md` and local `$SOPHNET_HOME/skills/<skill-name>/SKILL.md`.
3. If remote version is greater than local version, mark as `Need update`.
4. For install-by-name requests, check whether `skills/<skill-name>` exists in the default repo.
5. If found, install from the default repo.
6. If not found, install from another GitHub repo/path.
7. If fallback repo/path is missing, ask the user for `<owner>/<repo>` and `<path>`.
8. After showing grouped sections, guide the user with two options:
   install all pending skills, or install specific selected skills.
9. After successful install, tell the user: `🎉 恭喜！Sophnet Skills 现在已经可用了，快去体验一下吧！🚀`

## Scripts
Use these local scripts:
- `scripts/list-skills.py` (defaults to `DuffyCoder/awesome-sophnet-skills`, `skills`, `main`)
- `scripts/list-skills.py --format json`
- `scripts/install-skill-from-github.py --repo DuffyCoder/awesome-sophnet-skills --path skills/<skill-name>`
- `scripts/install-skill-from-github.py --repo DuffyCoder/awesome-sophnet-skills --path skills/<skill-1> skills/<skill-2> --replace`
- `scripts/install-skill-from-github.py --repo <owner>/<repo> --path <path/to/skill>`
- `scripts/install-skill-from-github.py --url https://github.com/<owner>/<repo>/tree/<ref>/<path>`

## Communication

When this skill starts, output approximately:
"""
Skills from {repo}:
1. skill-1 [not installed]
2. skill-2 [needs update]
3. ...

Not installed:
- ...

Need update:
- ...

Latest version:
- ...

Next step:
1. Install all pending skills
2. Install specific skills
Would you like to install all pending skills, or only specific ones?
"""

When fallback is needed, say clearly:
`<skill-name> is not available in DuffyCoder/awesome-sophnet-skills/skills. Provide another repo/path and I will install it from there.`

## Behavior and Options
- Defaults to direct download for public GitHub repos.
- If download fails with auth/permission errors, falls back to git sparse checkout.
- By default, aborts if the destination skill directory already exists.
- Use `--replace` to overwrite existing directories when updating installed skills.
- Installs into `$SOPHNET_HOME/skills/<skill-name>` (defaults to `~/.sophnet/skills`).
- Multiple `--path` values install multiple skills in one run, each named from the path basename unless `--name` is supplied.
- Options: `--ref <ref>` (default `main`), `--dest <path>`, `--method auto|download|git`.

## Notes

- Default listing is fetched from `https://api.github.com/repos/DuffyCoder/awesome-sophnet-skills/contents/skills?ref=main`. If unavailable, explain the error and stop.
- Version comparison depends on `metadata.version` in each skill `SKILL.md`.
- If local or remote `metadata.version` is missing, classify as `Need update` and mention missing version metadata.
- Private GitHub repos can be accessed via existing git credentials or optional `GITHUB_TOKEN`/`GH_TOKEN` for download.
- Git fallback tries HTTPS first, then SSH.
- Installed annotations come from `$SOPHNET_HOME/skills`.
