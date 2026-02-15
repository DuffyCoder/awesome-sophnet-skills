---
name: sophnet-image-edit
description: Use when a user requests SophNet image editing (image-to-image), including multi-image editing tasks (composition, style transfer, region swap) where all uploaded image paths must be resolved from Media Understanding logs (usually media/inbound/images/*) and passed in order to model Qwen-Image-Edit-2509.
metadata:
  short-description: Edit SophNet images with strict multi-image path/order handling
---

# SophNet Image Edit

## Overview
Edit existing images with SophNet shell scripts that handle task polling and structured output.

Script responsibilities:
- `edit_image.sh`: core API caller and polling loop, outputs `INPUT_IMAGE_COUNT`, `TASK_ID`, `STATUS`, and `IMAGE_URL`.
- `edit_and_preview.sh`: wrapper for local use, calls `edit_image.sh`, downloads first result, adds `PREVIEW_PATH`.

## When to Use
- User asks to edit or transform existing images with Sophnet.
- Task uses one or more source images (URL or uploaded local files).
- Task depends on image order/role, such as:
  - put part of image-2 into image-1
  - render image-2 with image-1 style
  - blend/composite many images into one result
- Do not use when the task is pure text-to-image generation; use `sophnet-image-generate`.

## Image Path Resolution
When users upload images in chat channels, files are usually saved under `media/inbound/images/` in the workspace. Use Media Understanding logs to get exact resolved paths.

Typical log pattern:
```
[Media Understanding] Resolved relative path: "media/inbound/images/xxx.jpg" -> "/absolute/path/to/workspace/media/inbound/images/xxx.jpg"
```

Path rules:
- `--image` accepts URL, data URI, or local file path.
- Local file paths are auto-converted to data URI by the script.
- The script submits request JSON via a temporary payload file (`curl --data-binary @file`) to avoid command-line argument length limits for large images.
- For multi-image tasks, pass every image explicitly and in required order.

## Multi-Image Rules
1. Keep source image order stable and explicit.
2. Bind prompt language to order (image-1, image-2, image-3...).
3. Do not drop “reference” images; pass all images used by the prompt.
4. Verify script output `INPUT_IMAGE_COUNT` equals expected image count before trusting results.

Recommended prompt pattern for multi-image tasks:
- `图1作为底图，图2提供主体元素，图3提供风格参考；将图2主体抠出放到图1右上角，并按图3风格整体渲染。`

## Quick Reference
| Goal | Command |
| --- | --- |
| Edit with one source | `bash {baseDir}/scripts/edit_and_preview.sh --prompt "..." --image "https://example.com/source.jpg"` |
| Edit with two sources (ordered) | `bash {baseDir}/scripts/edit_and_preview.sh --prompt "图1作为底图，将图2主体放入图1左下角" --image "media/inbound/images/img1.jpg" --image "media/inbound/images/img2.jpg"` |
| Style transfer across two images | `bash {baseDir}/scripts/edit_image.sh --prompt "使用图1的画风渲染图2内容" --image "/abs/path/style.jpg" --image "/abs/path/content.jpg"` |
| Many images via CSV | `bash {baseDir}/scripts/edit_image.sh --prompt "..." --images "media/inbound/images/a.jpg,media/inbound/images/b.jpg,https://example.com/c.jpg"` |
| Many images via list file | `bash {baseDir}/scripts/edit_image.sh --prompt "..." --images-file "/tmp/image-list.txt"` |
| Validate image count only | `bash {baseDir}/scripts/edit_image.sh --prompt "..." --images-file "/tmp/image-list.txt" --dry-run` |
| Show options | `bash {baseDir}/scripts/edit_image.sh --help` |

Notes:
- `--dry-run` does not require API key and is for input-count verification only.
- Prefer `--images-file` when handling many images or values that may contain commas.

`/tmp/image-list.txt` format example:
```text
# One image reference per line
media/inbound/images/base.jpg
media/inbound/images/object.png
https://example.com/style.jpg
```

## Implementation
1. Ensure `SOPH_API_KEY` is available. If missing, use `sophnet-key`.
2. Resolve all uploaded image paths from Media Understanding logs.
3. If this edit step follows `sophnet-image-generate`, prefer upstream `IMAGE_URL` for handoff; use `PREVIEW_PATH` only when local-file input is explicitly intended.
4. Build prompt with explicit image order semantics.
5. Run script with one `--image` per image, or `--images`, or `--images-file`.
6. For multi-image tasks, run once with `--dry-run` and confirm `INPUT_IMAGE_COUNT` matches intended image count.
7. Parse `TASK_ID`, `STATUS`, and `IMAGE_URL` outputs.
8. Use `PREVIEW_PATH` when present.

API payload shape:
- `model`: `Qwen-Image-Edit-2509`
- `input.prompt`: edit instruction with image-role semantics
- `input.images[]`: all source image refs in strict order
- `parameters`: `size`, `n`, `watermark`

## Common Mistakes
- Passing only one image for a multi-image prompt.
- Mentioning image-2/image-3 in prompt but not passing those images.
- Reordering `--image` arguments unintentionally.
- Ignoring `INPUT_IMAGE_COUNT` mismatch.
- Using non-existent local paths.
- In generate→edit workflows, defaulting to `PREVIEW_PATH` instead of `IMAGE_URL` without reason.
- Missing key setup: `Error: No API key provided.`
