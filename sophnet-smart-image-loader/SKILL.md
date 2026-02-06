---
name: sophnet-smart-image-loader
description: Use when an image must be displayed from URL or local path and the caller needs one path-resolution workflow with explicit success/failure output and cleanup handling.
metadata:
  short-description: Resolve image URL or path for local preview
---

# Smart Image Loader

## Overview
Normalize image loading for both web URLs and local files, then return a local file path ready for preview tooling.

## When to Use
- User asks to show/display/preview an image.
- Input may be URL (`http://`, `https://`) or local path.
- Caller needs a single output contract before invoking an image viewer.
- Do not use when image generation is required; use `sophnet-image-generate`.

## Quick Reference
| Goal | Command |
| --- | --- |
| Resolve URL or local path | `python3 {baseDir}/scripts/smart_image_loader.py <image_path_or_url>` |
| Show script usage | `python3 {baseDir}/scripts/smart_image_loader.py` |

## Implementation
1. Run the script with the raw user input.
2. Read output keys: `Status`, `Type`, `File Path`, `Cleanup Needed`.
3. On `Status: SUCCESS`, preview `File Path`.
4. If `Cleanup Needed: True`, remove temporary download artifacts after preview.

## Common Mistakes
- Trying to preview when `Status: FAILED`.
- Forgetting cleanup for URL downloads.
- Passing a relative local path from the wrong working directory.
