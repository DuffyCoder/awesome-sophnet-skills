---
name: sophnet-face-search
description: Face detection and similarity search using Sophnet API. Use when the user needs to find similar faces across multiple images, detect faces in photos, or compare face embeddings. Supports two-step workflow - extract query face embedding, then search for similar faces in a collection of images.
---
# Sophon Face Search

Search for similar faces across multiple images using face detection and embedding comparison.

## Overview

This skill provides face detection and similarity search capabilities using the Sophnet face detection API. It supports a two-step workflow:

1. **Extract query face**: Detect the largest face in a query image and extract its embedding
2. **Search similar faces**: Find similar faces in a collection of images by comparing embeddings

## Prerequisites

The skill uses `uv` for Python environment management and requires:
- Sophnet API key (obtained via the `sophnet-sophon-key` skill)
- Python 3.8+
- opencv-python-headless, numpy, requests

## Image Path Resolution

**Important:** When users upload images via webchat or other channels, Moltbot saves them to `media/inbound/images/` in the workspace. The system prompt includes media understanding logs that show the resolved absolute path.

Look for logs like:
```
[Media Understanding] Resolved relative path: "media/inbound/images/xxx.jpg" -> "/absolute/path/to/workspace/media/inbound/images/xxx.jpg"
```

## Workflow

### Step 1: Extract Query Face Embedding

Extract the largest face from a query image:

```bash
uv run --with opencv-python-headless --with numpy --with requests \
  {baseDir}/scripts/face_search.py base <query-image-path> \
  [--det-thr 0.7] [--output-dir <dir>]
```

**Parameters:**
- `query-image-path`: Path to the query image (prefer absolute path, e.g., `/absolute/path/to/workspace/media/inbound/images/xxx.jpg`)
- `--det-thr`: Detection confidence threshold (default: 0.7)
- `--output-dir`: Optional output directory for embedding JSON (recommended: `/tmp/face-search-output`)

**Output:**
- Embedding JSON file (e.g., `image_embedding.json`)
- Face preview image with bounding box (e.g., `image_face.jpg`)
- Console output includes `FACE_PREVIEW:<path>` marker for preview

**Important:** Always display the face preview image to the user using the `read` tool after this step.

### Step 2: Search for Similar Faces

Search for similar faces in a collection of images:

```bash
uv run --with opencv-python-headless --with numpy --with requests \
  {baseDir}/scripts/face_search.py search <query-embedding.json> <image1> <image2> ... \
  [--det-thr 0.5] [--threshold 0.5] [--output-dir <dir>]
```

**Parameters:**
- `query-embedding.json`: The embedding JSON from step 1 (absolute path, e.g., `/tmp/face-search-output/xxx_embedding.json`)
- `image1 image2 ...`: List of images to search (relative to workspace root or absolute paths)
- `--det-thr`: Detection confidence threshold (default: 0.5)
- `--threshold`: Similarity threshold (default: 0.5, range: 0-1)
- `--output-dir`: Optional output directory for embeddings

**Output:**
- List of matching images with similarity scores
- Console output includes `MATCHED_IMAGES:<paths>` marker
- Each match shows: image path, face index, similarity percentage

**Important:** Display preview images for all matched results using the `read` tool.

## API Key Management

Before running face search, obtain the Sophnet API key:

1. Use the `sophnet-sophon-key` skill to retrieve the API key
2. Set the environment variable: `export SOPH_API_KEY="<key>"`
3. The script will automatically use this environment variable

## Output Format Guidelines

When presenting results to the user:

- **List only**: image path and similarity percentage
- **Do NOT**: add image descriptions, interpretations, or conclusions like "是同一个人" or "不是同一个人"
- **Do**: display preview images for query face and all matched results
- **Format**: `<image-path> (人脸#<index>, 相似度: <percentage>%)`

Example output:
```
找到 2 个相似人脸:
  /path/to/image1.jpg (人脸#0, 相似度: 85.32%)
  /path/to/image2.jpg (人脸#0, 相似度: 72.15%)
```

## Example Usage

Complete workflow:

```bash
# Step 1: Extract query face
uv run --with opencv-python-headless --with numpy --with requests \
  {baseDir}/scripts/face_search.py base media/inbound/images/query.jpg \
  --output-dir /tmp/face-search-output

# Display the face preview to user
# (use read tool on the _face.jpg output from FACE_PREVIEW marker)

# Step 2: Search similar faces
uv run --with opencv-python-headless --with numpy --with requests \
  {baseDir}/scripts/face_search.py search \
  /tmp/face-search-output/query_embedding.json \
  media/inbound/images/photo1.jpg \
  media/inbound/images/photo2.jpg \
  media/inbound/images/photo3.jpg \
  --threshold 0.6 \
  --output-dir /tmp/face-search-output

# Display all matched image previews to user
# (use read tool on each matched image from MATCHED_IMAGES marker)
```

## Thresholds

- **Detection threshold** (`--det-thr`): Minimum confidence for face detection
  - Query: 0.7 (higher = more confident faces only)
  - Search: 0.5 (lower = detect more faces)
  
- **Similarity threshold** (`--threshold`): Minimum cosine similarity for matches
  - Default: 0.5 (50% similarity)
  - Range: 0.0 to 1.0
  - Higher values = stricter matching

## Notes

- The script uses opencv-python-headless (no GUI dependencies)
- Face embeddings are cached as JSON files for reuse
- Similarity is computed using cosine similarity between embeddings
- Only the largest face is extracted from the query image
- All faces above the detection threshold are searched in target images
