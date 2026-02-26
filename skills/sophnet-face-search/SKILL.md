---
name: sophnet-face-search
description: Search for similar faces in image directories using face detection and embedding comparison. Use when users want to find photos containing a specific person, search for similar faces across image collections, or identify matching faces in photo libraries. Supports automatic path extraction from logs (patterns like "Resolved relative path"), configurable similarity thresholds, and visual preview of query and result faces.
---

# Face Search

Search for similar faces in image directories using Sophnet's face detection API.

## Processing Mode

**STRICT SERIAL PROCESSING ONLY** - This skill must execute in a single, sequential operation:
- **NO sub-tasks** - Never spawn background sessions or use sessions_spawn
- **NO task splitting** - Process all images in one continuous run
- **NO parallel execution** - All face detection and comparison must be done serially
- Complete the entire search workflow before returning results to the user

## Prerequisites

- Python packages: opencv-python-headless, numpy, requests, sophnet-tools

## Usage

When a user wants to search for faces:

1. **Extract image path** from user input or recent logs (look for patterns like `Resolved relative path: "media/inbound/images/xxx.jpg"`)
2. **Run the search** using uv from /tmp to avoid workspace pyproject.toml conflicts:

```bash
uv run --with opencv-python-headless --with numpy --with requests \
  python {baseDir}/scripts/face_search.py \
  --image_path /absolute/path/to/query.jpg \
  --search_image_path /absolute/path/to/search/folder \
  --threshold 0.4
```

## Parameters

- `--image_path`: Query image containing the face to search for (required)
- `--search_image_path`: Directory to search for similar faces (required)
- `--det-thr`: Face detection threshold (default: 0.5)
- `--threshold`: Similarity threshold for matching (default: 0.4, range: 0.0-1.0)

## Output

The script outputs:
1. Query face preview with bounding box: `MEDIA:/path/to/query_face.jpg`
2. List of matching images with similarity scores
3. Each result shows: `MEDIA:/absolute/path/to/result.jpg`

**After the search completes, format the output as follows:**

```
查询人脸预览：
[Use read tool to display the query face (*_face.jpg)]

搜索到 N 个相似人脸：
[Use read tool to display each matching result image]

搜索到的图片列表：
/absolute/path/to/result1.jpg
/absolute/path/to/result2.png
/absolute/path/to/result3.jpg
```

**Important:**
- Always show absolute paths in the final list
- Use `read` tool to visually display both query face and all matching results
- Extract absolute paths from the script's MEDIA: output lines

## Path Extraction

When users provide images through chat, look for log patterns like:
```
Resolved relative path: "media/inbound/images/xxx.jpg" -> "/absolute/path/to/workspace/media/inbound/images/xxx.jpg"
```

Extract the absolute path (right side of `->`) for use with the script.

## Example Workflow

User: "Find photos with this person in my vacation folder"

1. Extract query image path from logs (or use most recent image from media/inbound/images)
2. Run: `uv run --with opencv-python-headless --with numpy --with requests python /path/to/face_search.py --image_path /path/to/query.jpg --search_image_path /path/to/vacation --threshold 0.4`
3. **Display the results with images:**
   - Use `read` tool to display the query face preview (the `*_face.jpg` file)
   - Use `read` tool to display each matching result image
   - This allows users to visually verify the matches

## Notes

- Always use absolute paths for reliability
- Lower threshold (e.g., 0.3) finds more matches but may include false positives
- Higher threshold (e.g., 0.7) is more strict but may miss some matches
- The script caches embeddings as JSON files to speed up repeated searches

## ⚠️ FORBIDDEN OPERATIONS

**Do NOT:**
- Spawn sub-agent sessions (sessions_spawn)
- Run multiple parallel face searches
- Split the task into separate operations
- Use background processes for face search

**ONLY:**
- Run the face_search.py script once with all required parameters
- Process all results in sequence
- Return complete results to the user in a single response
