#!/usr/bin/env python3
"""
Image generation via SophNet Gemini API.
Accepts a cover type (or explicit size) and prompt, generates an image,
uploads to OSS. Outputs machine-friendly COVER_TYPE, COVER_SIZE, STATUS,
and IMAGE_URL lines.

Style dimensions (palette, rendering, mood, layout) are injected into the
prompt automatically when specified via CLI flags.
"""

import argparse
import base64
import json
import math
import os
import sys
import tempfile

import requests
import sophnet_tools

from _shared import COVER_TYPES as _BASE_COVER_TYPES
from _shared import SAFETY_NEGATIVE_PROMPT, strip_oss_signature

API_URL = (
    "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/"
    "google/models/gemini-3.1-flash-image-preview:generateContent"
)

DEFAULT_NEGATIVE_PROMPT = SAFETY_NEGATIVE_PROMPT

# Gemini API needs aspect_ratio per cover type
_ASPECT_RATIOS = {
    # Actual ratio is ~2.35:1; 16:9 (1.78:1) is the closest the API supports.
    # The prompt text requests exact 900x383 to nudge the model.
    "wechat-header": "16:9",
    "wechat-square": "1:1",
    "xiaohongshu": "3:4",
    "guide": "3:4",
    "style": "1:1",
}

COVER_TYPES = {
    k: {**v, "aspect_ratio": _ASPECT_RATIOS[k]}
    for k, v in _BASE_COVER_TYPES.items()
}

PALETTES = {
    "warm": "Warm color palette: golden yellows, amber oranges, terracotta reds, honey tones. Evokes comfort and warmth.",
    "elegant": "Elegant palette: champagne gold, ivory, dusty rose, soft grey. Refined and sophisticated feel.",
    "cool": "Cool palette: ocean blues, mint greens, silver greys, icy whites. Clean and calming atmosphere.",
    "dark": "Dark palette: deep navy, charcoal, dark teal, muted burgundy. High contrast, dramatic mood.",
    "earth": "Earth palette: olive green, clay brown, sandstone, forest tones. Natural and organic feeling.",
    "vivid": "Vivid palette: saturated primary colors, bold contrasts, bright accents. High energy and eye-catching.",
    "pastel": "Pastel palette: soft pink, baby blue, lavender, mint. Gentle, dreamy, and delicate.",
    "mono": "Monochrome palette: shades of a single hue with tonal variation. Unified and striking.",
    "retro": "Retro palette: mustard yellow, burnt orange, avocado green, faded teal. 1970s nostalgic warmth.",
}

RENDERINGS = {
    "flat-vector": "Flat vector illustration style: clean geometric shapes, solid color fills, no gradients or textures, minimal line work.",
    "hand-drawn": "Hand-drawn illustration style: visible sketch lines, organic imperfections, ink-and-paper feel, slightly uneven edges.",
    "painterly": "Painterly style: visible brush strokes, rich textures, soft blended edges, oil or watercolor painting feel.",
    "digital": "Polished digital art style: smooth gradients, clean rendering, precise details, modern and refined.",
    "pixel": "Pixel art style: retro 8-bit aesthetic, blocky shapes, limited color palette, nostalgic gaming feel.",
    "chalk": "Chalk/chalkboard style: white and colored chalk on dark background, hand-lettered feel, educational aesthetic.",
}

MOODS = {
    "subtle": "Subtle mood: low contrast, muted tones, generous whitespace, understated and calm composition.",
    "balanced": "Balanced mood: moderate contrast, harmonious composition, professional and approachable.",
    "bold": "Bold mood: high contrast, saturated colors, dynamic composition, strong visual impact.",
}

LAYOUTS = {
    "bento-grid": "Bento grid layout: modular grid of varied-size cards, each containing a distinct piece of information.",
    "list": "List layout: enumerated items in a vertical sequence with icons or numbers.",
    "comparison": "Comparison layout: side-by-side or split-screen contrasting two options or concepts.",
    "flow": "Flow layout: connected steps or stages showing a process or timeline with directional arrows.",
    "mindmap": "Mind map layout: central concept radiating outward to connected branches and sub-topics.",
    "hub-spoke": "Hub-spoke layout: central element surrounded by related items in a radial arrangement.",
    "funnel": "Funnel layout: wide-to-narrow stages showing progressive filtering or conversion.",
    "dense-modules": "Dense modules layout: tightly packed information blocks with high data density, guide-style.",
}

STYLE_PRESETS = {
    "blueprint": {"palette": "dark", "rendering": "chalk", "mood": "bold"},
    "notion": {"palette": "mono", "rendering": "hand-drawn", "mood": "subtle"},
    "watercolor": {"palette": "pastel", "rendering": "painterly", "mood": "subtle"},
    "pop-art": {"palette": "vivid", "rendering": "flat-vector", "mood": "bold"},
    "vintage": {"palette": "retro", "rendering": "hand-drawn", "mood": "balanced"},
    "corporate": {"palette": "cool", "rendering": "flat-vector", "mood": "balanced"},
    "cozy": {"palette": "warm", "rendering": "painterly", "mood": "subtle"},
    "kawaii": {"palette": "pastel", "rendering": "flat-vector", "mood": "balanced"},
    "morandi": {"palette": "earth", "rendering": "hand-drawn", "mood": "subtle"},
}

STANDARD_RATIOS = ["1:1", "3:4", "4:3", "9:16", "16:9"]


def size_to_aspect_ratio(w, h):
    """Convert pixel dimensions to the closest standard aspect ratio."""
    target = w / h
    best = None
    best_diff = float("inf")
    for ratio_str in STANDARD_RATIOS:
        rw, rh = map(int, ratio_str.split(":"))
        ratio_val = rw / rh
        diff = abs(math.log(target) - math.log(ratio_val))
        if diff < best_diff:
            best_diff = diff
            best = ratio_str
    return best


def size_to_image_size(w, h):
    max_dim = max(w, h)
    if max_dim <= 512:
        return "512"
    return "1K"


def build_prompt(user_prompt, width, height, negative_prompt=None,
                 palette=None, rendering=None, mood=None, layout=None):
    merged_negative = DEFAULT_NEGATIVE_PROMPT
    if negative_prompt:
        merged_negative = f"{DEFAULT_NEGATIVE_PROMPT}, {negative_prompt}"

    parts = [
        f"Generate an image with these specifications:",
        f"- Desired dimensions: {width}x{height} pixels",
    ]

    if palette and palette in PALETTES:
        parts.append(f"- Color direction: {PALETTES[palette]}")
    if rendering and rendering in RENDERINGS:
        parts.append(f"- Rendering style: {RENDERINGS[rendering]}")
    if mood and mood in MOODS:
        parts.append(f"- Mood: {MOODS[mood]}")
    if layout and layout in LAYOUTS:
        parts.append(f"- Information layout: {LAYOUTS[layout]}")

    parts.extend([
        f"- {user_prompt}",
        f"- Content safety: The image must NOT contain any of the following: {merged_negative}.",
        "Generate only the image, no extra commentary.",
    ])
    return "\n".join(parts)


def call_gemini(api_key, prompt, aspect_ratio, image_size):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt}
            ]
        }],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
            }
        }
    }

    resp = requests.post(API_URL, json=payload, headers=headers, timeout=300)
    resp.raise_for_status()
    return resp.json()


def extract_image_b64(data):
    """Extract base64 image data from Gemini generateContent response."""
    candidates = data.get("candidates", [])
    for candidate in candidates:
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        for part in parts:
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and "data" in inline:
                mime = inline.get("mimeType", inline.get("mime_type", "image/png"))
                ext = mime.split("/")[-1].split(";")[0]
                return inline["data"], ext
    return None, None


def upload_b64_image(b64_data, ext="png"):
    try:
        raw = base64.b64decode(b64_data)
    except Exception as e:
        print(f"Warning: base64 decode failed: {e}", file=sys.stderr)
        return None

    fd, tmp_path = tempfile.mkstemp(suffix=f".{ext}", prefix="cover_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)

        signed_url = sophnet_tools.upload_oss(tmp_path)
        if not signed_url:
            print("Warning: upload_oss returned no signed URL", file=sys.stderr)
            return None
        return strip_oss_signature(signed_url)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def resolve_style_preset(preset_name):
    """Expand a style preset into palette/rendering/mood values."""
    preset = STYLE_PRESETS.get(preset_name)
    if not preset:
        return None, None, None
    return preset.get("palette"), preset.get("rendering"), preset.get("mood")


def main():
    type_names = ", ".join(f"{k} ({v['label']})" for k, v in COVER_TYPES.items())
    palette_names = ", ".join(PALETTES.keys())
    rendering_names = ", ".join(RENDERINGS.keys())
    mood_names = ", ".join(MOODS.keys())
    layout_names = ", ".join(LAYOUTS.keys())
    preset_names = ", ".join(STYLE_PRESETS.keys())

    parser = argparse.ArgumentParser(
        description="Generate images via SophNet Gemini API with style dimensions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"Cover types:\n  {type_names}\n\n"
            f"Palettes:\n  {palette_names}\n\n"
            f"Renderings:\n  {rendering_names}\n\n"
            f"Moods:\n  {mood_names}\n\n"
            f"Layouts (guide type only):\n  {layout_names}\n\n"
            f"Style presets (shorthand for palette+rendering+mood):\n  {preset_names}"
        ),
    )
    parser.add_argument("--type", required=True, choices=COVER_TYPES.keys(),
                        help="Cover type (determines image size and aspect ratio)")
    parser.add_argument("--prompt", required=True,
                        help="Image content description (scene, subject, atmosphere)")
    parser.add_argument("--size", default=None,
                        help="Override size as WxH or W*H (default: auto from --type)")
    parser.add_argument("--palette", default=None, choices=list(PALETTES.keys()),
                        help="Color palette direction")
    parser.add_argument("--rendering", default=None, choices=list(RENDERINGS.keys()),
                        help="Visual rendering style")
    parser.add_argument("--mood", default=None, choices=list(MOODS.keys()),
                        help="Overall mood intensity")
    parser.add_argument("--layout", default=None, choices=list(LAYOUTS.keys()),
                        help="Information layout (primarily for guide/infographic type)")
    parser.add_argument("--style-preset", default=None, choices=list(STYLE_PRESETS.keys()),
                        help="Style shorthand that sets palette+rendering+mood together")
    parser.add_argument("--negative-prompt", default=None,
                        help="Additional negative prompt terms")
    args = parser.parse_args()

    palette = args.palette
    rendering = args.rendering
    mood = args.mood

    if args.style_preset:
        p_palette, p_rendering, p_mood = resolve_style_preset(args.style_preset)
        if not palette:
            palette = p_palette
        if not rendering:
            rendering = p_rendering
        if not mood:
            mood = p_mood

    cover = COVER_TYPES[args.type]
    size_str = (args.size if args.size else cover["size"]).replace("x", "*").replace("×", "*")
    try:
        w, h = size_str.split("*")
        w, h = int(w.strip()), int(h.strip())
    except ValueError:
        print(f"Error: Invalid size format '{args.size or cover['size']}'. Use WxH (e.g. 900x383).",
              file=sys.stderr)
        sys.exit(1)

    aspect_ratio = cover.get("aspect_ratio") if not args.size else size_to_aspect_ratio(w, h)
    image_size = size_to_image_size(w, h)

    print(f"COVER_TYPE={args.type}")
    print(f"COVER_SIZE={w}*{h}")
    if palette:
        print(f"PALETTE={palette}")
    if rendering:
        print(f"RENDERING={rendering}")
    if mood:
        print(f"MOOD={mood}")
    if args.layout:
        print(f"LAYOUT={args.layout}")

    api_key = sophnet_tools.get_api_key()
    if not api_key:
        print("Error: No API key found. Set SOPH_API_KEY or configure via sophnet-key skill.",
              file=sys.stderr)
        sys.exit(1)

    prompt = build_prompt(
        args.prompt, w, h,
        negative_prompt=args.negative_prompt,
        palette=palette,
        rendering=rendering,
        mood=mood,
        layout=args.layout,
    )
    print("STATUS=generating", file=sys.stderr)

    try:
        result = call_gemini(api_key, prompt, aspect_ratio, image_size)
    except requests.RequestException as e:
        print(f"Error: SophNet Gemini API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    b64_data, ext = extract_image_b64(result)
    if not b64_data:
        print("Error: no image data found in response.", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    signed_url = upload_b64_image(b64_data, ext or "png")
    if signed_url:
        print("STATUS=succeeded")
        print(f"IMAGE_URL={signed_url}")
    else:
        print("Error: failed to upload image to OSS.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
