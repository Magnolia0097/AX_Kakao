#!/usr/bin/env python3
"""Render a saved conversation log (JSONL) into a human-readable Markdown file.

Faithful 1:1 format conversion, not a summary: every conversation turn that the
official collector (tools/save_log.py) keeps is rendered in order, with its text
reproduced verbatim. No turn is dropped, truncated, reworded, or reordered — only
the wrapper format changes from JSONL to Markdown (an allowed submission format).

Usage:
    python3 tools/log_to_md.py logs/claude-code/<session_id>.jsonl
    # -> writes logs/claude-code/<session_id>.md
Optionally pass an explicit output path as the second argument.
"""
import json
import os
import sys

_ROLE_HEADING = {"user": "## 👤 User", "assistant": "## 🤖 Assistant"}


def _content_text(content) -> str:
    """message content (str or block list) -> conversation text only (verbatim)."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [b["text"] for b in content
                 if isinstance(b, dict) and b.get("type") == "text"
                 and isinstance(b.get("text"), str)]
        return "\n\n".join(p.strip() for p in parts).strip()
    return ""


def render(jsonl_path: str) -> str:
    session = os.path.splitext(os.path.basename(jsonl_path))[0]
    lines = [f"# 대화 로그 — session {session}", "", "> tool: claude-code", ""]
    with open(jsonl_path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except (ValueError, TypeError):
                continue
            role = obj.get("type")
            if role not in _ROLE_HEADING:
                continue
            message = obj.get("message")
            if not isinstance(message, dict):
                continue
            text = _content_text(message.get("content"))
            if not text:
                continue
            lines.append(_ROLE_HEADING[role])
            lines.append("")
            lines.append(text)
            lines.append("")
            lines.append("---")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: log_to_md.py <input.jsonl> [output.md]", file=sys.stderr)
        return 1
    src = sys.argv[1]
    if not os.path.isfile(src):
        print(f"log_to_md: input not found: {src}", file=sys.stderr)
        return 1
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".md"
    with open(dest, "w", encoding="utf-8") as out:
        out.write(render(src))
    print(f"log_to_md: wrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
