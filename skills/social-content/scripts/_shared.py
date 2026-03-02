"""Shared constants and utilities for image generation providers."""

import requests

COVER_TYPES = {
    "wechat-header": {
        "size": "900*383",
        "label": "WeChat header (900x383)",
    },
    "wechat-square": {
        "size": "200*200",
        "label": "WeChat square preview (200x200)",
    },
    "xiaohongshu": {
        "size": "1080*1440",
        "label": "Xiaohongshu cover (1080x1440)",
    },
    "guide": {
        "size": "1080*1440",
        "label": "Guide / infographic (1080x1440)",
    },
    "style": {
        "size": "1024*1024",
        "label": "Stylized photo (1024x1024)",
    },
}

SAFETY_NEGATIVE_PROMPT = (
    "nsfw, nudity, nude, naked, sexual, erotic, pornographic, gore, blood, violence, "
    "bloody, corpse, dead body, weapon, gun, knife, drugs, smoking, alcohol, gambling, "
    "politically sensitive, national flag, national emblem, political leader, "
    "religious symbol, hate symbol, discrimination, racist, offensive, disturbing, "
    "child exploitation, terrorism, self-harm"
)

# Extra terms for APIs where text rendering in images is undesirable
TEXT_NEGATIVE_PROMPT = (
    "text, words, letters, numbers, alphabet, characters, writing, caption, title, "
    "subtitle, label, logo, watermark, signature, stamp, typographic, font, inscription, "
    "banner, sign, signage, handwriting, calligraphy"
)


def strip_oss_signature(url):
    """Remove OSS signature query params to get a publicly accessible bare URL.
    SophNet's bucket allows public read, but broken signatures cause 403."""
    if not url or "?" not in url:
        return url
    bare = url.split("?")[0]
    try:
        r = requests.head(bare, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            return bare
    except requests.RequestException:
        pass
    return url
