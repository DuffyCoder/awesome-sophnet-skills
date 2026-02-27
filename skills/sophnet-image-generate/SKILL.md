---
name: sophnet-image-generate
description: Use when a user requests Sophnet text-to-image generation, needs model selection across Z-Image-Turbo/Qwen-Image/Qwen-Image-Plus, or reports polling/output issues such as missing IMAGE_URL or PREVIEW_PATH.
metadata:
  short-description: Generate Sophnet images with stable polling outputs
---

# Sophnet Image Generate

## Overview
Generate Sophnet images with Python scripts that handle task polling and structured output.

Script responsibilities:
- `generate_image.py`: core API caller and polling loop, outputs machine-friendly `TASK_ID`, `STATUS`, and `IMAGE_URL`.
- `generate_and_preview.sh`: wrapper for local use, calls `generate_image.py`, downloads first image, adds `PREVIEW_PATH`.

## When to Use
- User asks to generate an image with Sophnet models.
- Caller needs stable outputs like `TASK_ID`, `STATUS`, `IMAGE_URL`, `PREVIEW_PATH`.
- Prompt includes model choice (`Z-Image-Turbo`, `Qwen-Image`, `Qwen-Image-Plus`).
- Do not use when the task is only to display an existing image URL/path; use `sophnet-smart-image-loader`.

## Quick Reference
| Goal | Command |
| --- | --- |
| Generate + local preview path | `bash {baseDir}/scripts/generate_and_preview.sh --prompt "..."` |
| Generate URLs only | `uv run --project {baseDir} python {baseDir}/scripts/generate_image.py --prompt "..."` |
| Show script options | `uv run --project {baseDir} python {baseDir}/scripts/generate_image.py --help` |

Recommended defaults:
- Use `generate_and_preview.sh` for interactive local image preview.
- Use `generate_image.py` for automation/CI or when download is not needed.

## Implementation
1. Run the script with `--prompt`.
2. Parse output lines by key prefix.
3. Use `IMAGE_URL` to share with users (publicly accessible). Use `PREVIEW_PATH` for local image preview when present.

## Common Mistakes
- Assuming `PREVIEW_PATH` exists when using `generate_image.py`.
