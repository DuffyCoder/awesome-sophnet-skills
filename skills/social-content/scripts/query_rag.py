#!/usr/bin/env python3
"""
Query the SophNet RAG knowledge base via chat completions API.
Uses sophnet_tools.get_api_key() for authentication.

Usage:
  uv run --with requests --with sophnet-tools \
    python query_rag.py --query "你的问题"
"""
import argparse
import json
import sys
import threading
import time
from typing import Optional

import requests
import sophnet_tools

API_URL = "https://www.sophnet.com/api/open-apis/v1/chat/completions"
# Model ID format: "<model_name>:<knowledge_base_id>"
MODEL = "GLM-5:y2b8n18wa2tK37Ra4syU2"
DEFAULT_SYSTEM_PROMPT = "你是一个专业的企业知识助手，请根据知识库中的信息准确回答问题。"
DEFAULT_TIMEOUT = 180
MAX_RETRIES = 3
RETRY_DELAY = 5


def _flush_print(msg, **kwargs):
    print(msg, **kwargs)
    sys.stdout.flush()
    if kwargs.get("file"):
        kwargs["file"].flush()


def query_rag(query: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT,
              raw: bool = False, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    api_key = sophnet_tools.get_api_key()
    if not api_key:
        print("Error: No API key found. Set SOPH_API_KEY or configure via sophnet-key skill.", file=sys.stderr)
        sys.exit(1)

    _flush_print(f"[RAG] Querying knowledge base (timeout={timeout}s) ...")

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "model": MODEL,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start = time.time()
            done_event = threading.Event()

            def _heartbeat():
                while not done_event.is_set():
                    if done_event.wait(10):
                        break
                    elapsed = time.time() - start
                    _flush_print(f"[RAG] Still waiting for API response ({elapsed:.0f}s elapsed, normal range 30-90s — do NOT kill this process)")

            hb = threading.Thread(target=_heartbeat, daemon=True)
            hb.start()
            try:
                resp = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
            finally:
                done_event.set()
                hb.join(timeout=2)

            elapsed = time.time() - start
            if resp.status_code >= 500:
                last_error = f"HTTP {resp.status_code} — {resp.text[:300]}"
                if attempt < MAX_RETRIES:
                    _flush_print(f"[RAG] Server error (HTTP {resp.status_code}), retrying in {RETRY_DELAY}s ... (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                    continue
                print(f"Error: {last_error}", file=sys.stderr)
                sys.exit(1)
            resp.raise_for_status()
            _flush_print(f"[RAG] Response received in {elapsed:.1f}s.")
            break
        except requests.exceptions.Timeout:
            done_event.set()
            last_error = f"Request timed out after {timeout}s"
            if attempt < MAX_RETRIES:
                _flush_print(f"[RAG] Timeout, retrying in {RETRY_DELAY}s ... (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
                continue
            print(f"Error: {last_error}.", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            done_event.set()
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    data = resp.json()

    if raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return None

    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})

    content = message.get("content")
    if not content:
        print("Error: Unexpected response format.", file=sys.stderr)
        print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    output_parts = [content]

    # Append reference sources if present (RAG retrieval results)
    refs = choice.get("refs", [])
    if refs:
        output_parts.append("")
        output_parts.append("---")
        output_parts.append(f"References ({len(refs)} sources):")
        for ref in refs:
            idx = ref.get("index", "?")
            title = ref.get("title", "unknown")
            output_parts.append(f"  [{idx}] {title}")

    return "\n".join(output_parts)


def main():
    parser = argparse.ArgumentParser(description="Query SophNet RAG knowledge base")
    parser.add_argument("--query", required=True, help="The question to ask the knowledge base")
    parser.add_argument("--system-prompt", default=DEFAULT_SYSTEM_PROMPT, help="Override the default system prompt")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON response")
    args = parser.parse_args()

    result = query_rag(args.query, system_prompt=args.system_prompt,
                       raw=args.raw, timeout=args.timeout)
    if result is not None:
        print(result)


if __name__ == "__main__":
    main()
