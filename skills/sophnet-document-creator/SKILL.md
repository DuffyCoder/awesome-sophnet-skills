---
name: sophnet-document-creator
description: Use when a user needs to create DOCX or PPTX files from text or markdown and optionally upload outputs to Sophnet OSS with signed URLs. Handles local file generation, uv-managed isolated Python dependencies (no pip required), structured script outputs, and Sophnet API key resolution through SOPH_API_KEY or Moltbot config fallback.
---

# Sophnet Document Creator

Create DOCX/PPTX files from inline content or markdown, then optionally upload the generated file to Sophnet OSS. Manage Python dependencies with a uv-managed isolated environment under this skill directory (`.venv`) so workflows do not depend on `pip`.

## Scripts

- `scripts/create_document.py`: Build local `docx` or `pptx` file and print structured output.
- `scripts/ensure_uv_env.sh`: Create/sync a skill-local uv environment and dependencies.
- `scripts/upload_file.sh`: Upload a local file to Sophnet and print `DOWNLOAD_URL`.
- `scripts/create_and_upload.sh`: End-to-end wrapper for creation + optional upload.
- `scripts/resolve_api_key.sh`: Resolve Sophnet API key using the same priority used across Sophnet skills.

## API Key Resolution

Use this order:

1. CLI `--api-key` (for upload wrappers)
2. `SOPH_API_KEY` environment variable
3. `sophnet-sophon-key/scripts/get-key.sh --output-quiet` when available
4. Config fallback (`MOLTBOT_CONFIG`, `~/.clawdbot/moltbot.json`, `~/.moltbot/moltbot.json`, `~/.openclaw/openclaw.json`)

If unresolved, stop and instruct the caller to run `sophnet-sophon-key`.

## Quick Reference

| Goal | Command |
| --- | --- |
| Prepare uv environment | `bash {baseDir}/scripts/ensure_uv_env.sh` |
| Create DOCX only | `uv run --project {baseDir} python {baseDir}/scripts/create_document.py docx --title "Project Brief" --markdown ./brief.md` |
| Create PPTX only | `uv run --project {baseDir} python {baseDir}/scripts/create_document.py pptx --title "Quarterly Review" --markdown ./slides.md --slides 8` |
| Create and upload (no local file persisted) | `bash {baseDir}/scripts/create_and_upload.sh --type docx --title "Spec" --markdown ./spec.md` |
| Create only and keep local file | `bash {baseDir}/scripts/create_and_upload.sh --type docx --title "Spec" --markdown ./spec.md --no-upload --keep-local` |
| Create and upload (keep local file) | `bash {baseDir}/scripts/create_and_upload.sh --type docx --title "Spec" --markdown ./spec.md --keep-local` |
| Upload existing file | `bash {baseDir}/scripts/upload_file.sh --file ./Spec_20260206_120000.docx` |

## Output Contract

`create_document.py` prints:
- `FILE_PATH=<absolute-path>`
- `FILE_TYPE=docx|pptx`
- `FILE_NAME=<basename>`

`upload_file.sh` prints:
- `FILE_PATH=<absolute-path>`
- `DOWNLOAD_URL=<https://...>`

`create_and_upload.sh` prints creation output plus:
- `UPLOAD_STATUS=uploaded`
- `DOWNLOAD_URL=<https://...>`
- `LOCAL_FILE_STATUS=deleted` (default)

When `--keep-local` is set, `create_and_upload.sh` also prints:
- `FILE_PATH=<absolute-path>`

When `--no-upload --keep-local` is set, `create_and_upload.sh` prints:
- `UPLOAD_STATUS=skipped`
- `FILE_PATH=<absolute-path>`

When upload fails, `create_and_upload.sh` prints:
- `UPLOAD_STATUS=failed`
- `ERROR=missing_api_key|upload_failed|missing_download_url`

## Execution Rules

1. Generate locally as a temporary step, upload, then delete local file by default.
2. Use `uv` to manage the skill-local Python environment; do not rely on `pip`.
3. Preserve deterministic key/value stdout format for machine parsing.
4. Keep stderr for diagnostics only.
5. On key or dependency errors, fail fast with actionable instructions.
6. Return only real `DOWNLOAD_URL` from command output; never return hypothetical URL examples as final result.
7. Use the exact `DOWNLOAD_URL` value when replying. Do not reconstruct from file name, do not remove query parameters, and do not shorten the link.
