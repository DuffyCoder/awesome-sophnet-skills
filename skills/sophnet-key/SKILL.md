---
name: sophnet-key
description: Configure and manage SophNet API Key. Automatically reads from Moltbot config or guides users through setup. Use when SOPH_API_KEY environment variable is missing or when helping users configure their SophNet API credentials.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔑",
        "requires": { "env": ["SOPH_API_KEY"], "bins": ["bash"] },
        "primaryEnv": "SOPH_API_KEY",
      },
  }
---

# SophNet Key

## Overview

Resolve and persist `SOPH_API_KEY` for SophNet-authenticated scripts.

## When to Use

- A script fails with missing/invalid API key errors.
- `SOPH_API_KEY` exists in config but is not exported in current shell.
- Key works in one terminal but disappears in new sessions.
- Do not use when key is already present and valid in environment.

## Quick Reference

| Goal                         | Command                                            |
| ---------------------------- | -------------------------------------------------- |
| Check and resolve key        | `bash {baseDir}/scripts/get-key.sh`                |
| Print key only (for scripts) | `bash {baseDir}/scripts/get-key.sh --output-quiet` |
| Interactive persistent setup | `bash {baseDir}/scripts/setup-key.sh`              |

Resolution order:

1. Existing `SOPH_API_KEY` in environment.
2. Moltbot config (`MOLTBOT_CONFIG` or `~/.clawdbot/moltbot.json`).
3. Interactive setup flow.

## Implementation

1. Run `get-key.sh` first.
2. If unresolved, run `setup-key.sh` and reload shell profile.
3. Retry the original caller command.

## Common Mistakes

- Expecting persistence without reloading shell profile.
- Using normal output mode in automation that expects raw key value only.
