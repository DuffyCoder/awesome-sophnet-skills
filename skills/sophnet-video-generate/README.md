# Video Generation Skill

Generate videos using Sophnet Video Generation API.

## Features

- **Text-to-video**: Generate videos from text prompts
- **Image-to-video**: Generate videos from first frame image
- **Image-to-video (first + last)**: Generate videos with transition between two images
- **Multiple models**: Seedance-1.5-Pro, Wan2.6-T2V/I2V, Wan2.2-T2V/I2V-A14B, ViduQ2-turbo
- **Customizable resolution**: 480P, 720P, 1080P
- **Customizable duration**: 1-12 seconds depending on model

## Requirements

- Python 3.8+
- uv (for dependency management)
- Sophnet API Key (managed by sophon-key skill)



## Usage

```bash
uv run --no-build-isolation python scripts/generate_video.py --prompt "your prompt"
```

## Examples

### Text-to-video
```bash
uv run --no-build-isolation python scripts/generate_video.py --prompt "A serene sunset over the ocean"
```

### Image-to-video with first frame
```bash
uv run --no-build-isolation python scripts/generate_video.py \
  --first-frame "https://example.com/image.jpg" \
  --prompt "Camera pans slowly"
```

### Text-to-video with custom model and resolution
```bash
uv run --no-build-isolation python scripts/generate_video.py \
  --prompt "Dramatic mountain landscape" \
  --model Wan2.6-T2V \
  --size "1920*1080" \
  --duration 10
```

### Generate video and upload to OSS
```bash
uv run --no-build-isolation python scripts/generate_video.py \
  --prompt "Your prompt" \
  --upload-oss
```
The script will:
1. Generate the video
2. Download it locally
3. Upload to OSS
4. Return both `VIDEO_URL` (original) and `OSS_URL` (uploaded)
Use `OSS_URL` for sharing via message tool.

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
- `ViduQ2-turbo`: 动态判断

## Default Behavior

If not specified:
- **Model**: `ViduQ2-turbo`
- **Resolution**: `1280*720` (720P)
- **Duration**: `5` (auto-select for ViduQ2-turbo)

## API Integration

This skill integrates with the Sophnet Video Generation API:
- Endpoint: `https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator/generate`
- Method: `POST` for creating tasks, `GET` for querying status
- Authentication: Bearer token (API key)

## Output

The script outputs:
- `TASK_ID`: Task identifier
- `STATUS`: Task status (succeeded)
- `VIDEO_URL`: URL to the generated video (from API)
- `OSS_URL`: Uploaded OSS URL (if `--upload-oss` specified)
- `LOCAL_PATH`: Local path (if `--output-file` or `--upload-oss` specified)
- Generation parameters summary

## OSS Upload Feature

When generating videos for sharing via the `message` tool, use the `--upload-oss` flag:

```bash
uv run python scripts/generate_video.py --prompt "..." --upload-oss
```

This will:
1. Generate the video
2. Download it to a temporary file
3. Upload it to OSS
4. Return an `OSS_URL` that can be used with the message tool

Example usage with message tool:
```python
# Run video generation
output = subprocess.run([
    "uv", "run", "--no-build-isolation", "python", "scripts/generate_video.py",
    "--prompt", "A beautiful sunset",
    "--upload-oss"
], capture_output=True, text=True)

# Extract OSS_URL
import re
match = re.search(r"OSS_URL=(.+)", output.stdout)
if match:
    oss_url = match.group(1)
    # Use with message tool
    message(action=send, target=..., media=oss_url, message="Video link")
```

## Script Options

See `uv run generate-video --help` for all options.