---
name: sophnet-image-generate
description: Use when a user requests Sophnet text-to-image generation, needs model selection across Z-Image-Turbo/Qwen-Image/Qwen-Image-Plus, or reports polling/output issues such as missing IMAGE_URL or PREVIEW_PATH.
metadata:
  short-description: Generate Sophnet images with stable polling outputs
---

# Sophnet Image Generate

## Overview
Generate Sophnet images with shell scripts that handle task polling and structured output.

Script responsibilities:
- `generate_image.sh`: core API caller and polling loop, outputs machine-friendly `TASK_ID`, `STATUS`, and `IMAGE_URL`.
- `generate_and_preview.sh`: wrapper for local use, calls `generate_image.sh`, downloads first image, adds `PREVIEW_PATH`.

## When to Use
- User asks to generate an image with Sophnet models.
- Caller needs stable outputs like `TASK_ID`, `STATUS`, `IMAGE_URL`, `PREVIEW_PATH`.
- Prompt includes model choice (`Z-Image-Turbo`, `Qwen-Image`, `Qwen-Image-Plus`).
- Do not use when the task is only to display an existing image URL/path; use `sophnet-smart-image-loader`.

## Quick Reference
| Goal | Command |
| --- | --- |
| Generate + local preview path | `bash {baseDir}/scripts/generate_and_preview.sh --prompt "..."` |
| Generate URLs only | `bash {baseDir}/scripts/generate_image.sh --prompt "..."` |
| Show script options | `bash {baseDir}/scripts/generate_image.sh --help` |

Recommended defaults:
- Use `generate_and_preview.sh` for interactive local image preview.
- Use `generate_image.sh` for automation/CI or when download is not needed.

## Implementation
1. Ensure `SOPH_API_KEY` is available. If missing, use `sophnet-sophon-key`.
2. Run the script with `--prompt`.
3. Parse output lines by key prefix.
4. Return `IMAGE_URL` values to the user and use `PREVIEW_PATH` for local image preview when present.

## Common Mistakes
- Missing key setup: `Error: No API key provided.`
- Assuming `PREVIEW_PATH` exists when using `generate_image.sh`.
