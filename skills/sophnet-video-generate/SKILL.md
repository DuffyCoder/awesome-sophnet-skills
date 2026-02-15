---
name: video-generation
description: Generate videos using SophNet Video Generation API. Supports text-to-video, image-to-video (first frame), and image-to-video (first + last frame). Default model: Seedance-1.5-Pro with 720p (1280*720) resolution. Polls for completion with 5-minute timeout. Use when user asks to generate videos, create videos from text or images.
---

# SophNet Video Generation

Generate videos using the SophNet Video Generation API with support for multiple models and modes.

## 前置检查

Ensure `SOPH_API_KEY` is available. If missing, use `sophnet-key`.

## Quick Start

Run the video generation script. There are two options:

**Option 1: Using uv (recommended, when available)**
```bash
cd "{baseDir}" && uv run --no-build-isolation python scripts/generate_video.py --prompt "your prompt"
```

**Option 2: Using Python directly (fallback)**
```bash
python3 {baseDir}/scripts/generate_video.py --prompt "your prompt"
```

This will:
1. Generate the video via SophNet API
2. Poll for task completion (every 5 seconds, 5-minute timeout)
3. Return the video URL and generation parameters
4. Optionally download the video locally

## Script Options

- `--prompt TEXT` (optional): Text prompt for text-to-video or to guide image-to-video
- `--negative-prompt TEXT` (optional): Negative prompt
- `--model MODEL` (optional): Model name. Default: `Seedance-1.5-Pro`
- `--size SIZE` (optional): Resolution. Default: `1280*720`
  - 480P: `832*480`, `480*332`, `640*640`
  - 720P: `1280*720`, `720*1280`, `960*960`, `1088*832`, `832*1088`
  - 1080P: `1920*1080`, `1080*1920`, `1440*1440`, `1632*1248`, `1248*1632`
- `--duration SECONDS` (optional): Video duration in seconds. Default: `-1` (auto-select)
  - Seedance-1.5-Pro: 4-12 or -1 (auto, default)
  - Others: 1 or 5
- `--first-frame URL` (optional): First frame image URL for image-to-video
- `--last-frame URL` (optional): Last frame image URL for image-to-video (Wan2.2-I2V-A14B)
- `--generate-audio` (optional): Generate audio (Seedance-1.5-Pro only)
- `--draft` (optional): Enable draft mode (Seedance-1.5-Pro only)
- `--api-key KEY` (optional): Override API key
- `--output-file PATH` (optional): Save downloaded video to this path
- `--upload-oss` (optional): Upload generated video to OSS and return OSS URL
- `--help`: Show help message

## Supported Models

### 万相系列
- `Wan2.6-T2V`: 文生视频
- `Wan2.6-I2V`: 图生视频

### 开源模型
- `Wan2.2-T2V-A14B`: 文生视频 (开源)
- `Wan2.2-I2V-A14B`: 图生视频 (开源)

### 字节跳动系列
- `Seedance-1.5-Pro`: 动态判断 (默认)

### 生数系列
- `ViduQ2-pro-fast`: 动态判断

## Output Contract

The script prints:
- `TASK_ID=...`
- `STATUS=succeeded`
- `VIDEO_URL=...` (original API video URL)
- `OSS_URL=...` (if `--upload-oss` specified, uploaded OSS URL)
- `LOCAL_PATH=...` (if `--output-file` or `--upload-oss` specified)
- Generation parameters summary

Note: When `--upload-oss` is used, the final video link shown to users should be the `OSS_URL`.

## Agent Usage

When generating videos for users:

1. Determine the mode:
   - **Text-to-video**: Use `--prompt`
   - **Image-to-video (first frame only)**: Use `--first-frame` + `--prompt`
   - **Image-to-video (first + last frames)**: Use `--first-frame` + `--last-frame` + `--prompt`

2. Run the script:
   ```bash
   cd "{baseDir}" && uv run --no-build-isolation python scripts/generate_video.py --prompt "your prompt"
   ```

3. Extract the `VIDEO_URL` from the output

4. Provide feedback to the user:
   - Show the generation parameters used
   - Share the video link
   - If the user didn't specify a model, mention other available models

5. Example response:
   ```
   视频生成完成！

   生成参数：
   - 模型：Seedance-1.5-Pro
   - 分辨率：1280*720 (720P)
   - 时长：5秒
   - 提示词：A serene sunset over the ocean

   视频链接：https://...

   其他支持的模型还有：
   - Wan2.6-T2V (文生视频)
   - Wan2.6-I2V (图生视频)
   - Wan2.2-T2V-A14B (文生视频，开源)
   - Wan2.2-I2V-A14B (图生视频，开源)
   - ViduQ2-pro-fast (文生视频 + 图生视频)

   下次可以直接指定模型和参数来生成，例如：
   --model Wan2.6-T2V --size "1920*1080" --duration 10
   ```

6. If you want to share the video with users via `message` tool, use `--upload-oss`:
   ```bash
   cd "{baseDir}" && uv run --no-build-isolation python scripts/generate_video.py --prompt "..." --upload-oss
   ```
   Then extract `OSS_URL` from output and use with message tool:
   ```
   message(action=send, target=..., media=OSS_URL, message="视频链接")
   ```

## Examples

### Text-to-video with defaults
```bash
cd "{baseDir}" && uv run --no-build-isolation python scripts/generate_video.py \
  --prompt "A serene sunset over the ocean"
```

### Image-to-video with first frame
```bash
cd "{baseDir}" && uv run --no-build-isolation python scripts/generate_video.py \
  --first-frame "https://example.com/image.jpg" \
  --prompt "Camera pans slowly to the right"
```

### Text-to-video with custom model and resolution
```bash
cd "{baseDir}" && uv run --no-build-isolation python scripts/generate_video.py \
  --prompt "Dramatic mountain landscape" \
  --model Wan2.6-T2V \
  --size "1920*1080" \
  --duration 10
```

### Image-to-video with first and last frames
```bash
cd "{baseDir}" && uv run --no-build-isolation python scripts/generate_video.py \
  --first-frame "https://example.com/start.jpg" \
  --last-frame "https://example.com/end.jpg" \
  --prompt "Smooth transition between frames" \
  --model Wan2.2-I2V-A14B
```

## Workflow

1. Build request body based on input mode (text-to-video or image-to-video)
2. POST create-task with model and content
3. Poll GET task status every 5 seconds until `succeeded`
4. Extract `video_url` and generation parameters
5. Return results to user
6. Optionally download video locally

## Default Behavior

If user doesn't specify:
- **Model**: Uses `Seedance-1.5-Pro`
- **Resolution**: Uses `1280*720` (720P)
- **Duration**: Uses `-1` (auto-select for Seedance-1.5-Pro)
- **Parameters**: Uses each model's default parameters

## Common Errors

- `Error: No API key provided` -> Run `sophon-key` setup or set `SOPH_API_KEY`
- `Error: Timeout after 300s` -> Video generation took too long, task may still be running
- `Error: No video URL found` -> Check task response or try again
- `Error: Failed to create task` -> Check API key permissions, model support, or request format

## 注意事项

- **前置检查**：调用 `sophon-key` skill，检测并配置 SOPH_API_KEY 环境变量
- **默认模型**：Seedance-1.5-Pro，分辨率 1280*720 (720P)
- **超时时间**：5分钟 (300秒)
- **轮询间隔**：5秒
- **异步任务**：视频生成是异步的，需要轮询查询状态

## Environment Setup

This skill requires the `requests` library. It can be installed via:
- `uv sync` (in the skill directory)
- `pip install requests` (if using Python directly)

If you encounter uv build errors related to workspace packages, use Python directly as a fallback.