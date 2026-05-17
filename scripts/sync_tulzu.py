#!/usr/bin/env python3
"""
Pull latest templates from claude-md-starters and update
tulzu/public/tools/claude-md-generator.html in the TulZu repo.

Replaces JS content between:
  // ── AUTO-SYNC START
  // ── AUTO-SYNC END

Requires TULZU_PAT secret (GitHub PAT with repo write access to TulZu).
"""

import os
import re
import json
import base64
import subprocess
import urllib.request
from pathlib import Path

TULZU_REPO  = "sanjeevnair/TulZu"
TULZU_FILE  = "tulzu/public/tools/claude-md-generator.html"
STARTERS_RAW = "https://raw.githubusercontent.com/sanjeevnair/claude-md-starters/main/templates"
TULZU_PAT   = os.environ.get("TULZU_PAT", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

SYNC_START = "// ── AUTO-SYNC START — do not edit below this line manually ───────────────────"
SYNC_END   = "// ── AUTO-SYNC END ─────────────────────────────────────────────────────────────"


def fetch_raw(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-md-starters-sync"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def escape_for_js_template(text: str) -> str:
    """Escape content so it's safe inside a JS backtick template literal."""
    text = text.replace("\\", "\\\\")          # backslashes first
    text = text.replace("`", "\\`")             # backticks
    text = text.replace("${", "\\${")           # template interpolations
    return text


def build_js_block(templates: dict[str, str], addons: dict[str, str]) -> str:
    """Rebuild the JS BASE + ADDONS block from template content."""
    lines = [
        SYNC_START,
        "// Source: github.com/sanjeevnair/claude-md-starters",
        "",
        "const BASE = {",
    ]

    for key, content in templates.items():
        escaped = escape_for_js_template(content)
        lines.append(f"  {repr(key)}: `{escaped}`,")
        lines.append("")

    lines.append("};")
    lines.append("")
    lines.append("const ADDONS = {")

    for key, content in addons.items():
        escaped = escape_for_js_template(content)
        lines.append(f"  {repr(key)}: `{escaped}`,")
        lines.append("")

    lines.append("};")
    lines.append("")
    lines.append(SYNC_END)

    return "\n".join(lines)


def get_tulzu_file() -> tuple[str, str]:
    """Fetch current file content + SHA from TulZu repo."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{TULZU_REPO}/contents/{TULZU_FILE}",
        headers={
            "Authorization": f"Bearer {TULZU_PAT or GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "claude-md-starters-sync",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())

    content = base64.b64decode(data["content"]).decode("utf-8")
    sha = data["sha"]
    return content, sha


def put_tulzu_file(content: str, sha: str, message: str) -> None:
    """Update file in TulZu repo via GitHub API."""
    payload = json.dumps({
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "sha": sha,
        "committer": {
            "name": "github-actions[bot]",
            "email": "github-actions[bot]@users.noreply.github.com",
        }
    }).encode()

    req = urllib.request.Request(
        f"https://api.github.com/repos/{TULZU_REPO}/contents/{TULZU_FILE}",
        data=payload,
        method="PUT",
        headers={
            "Authorization": f"Bearer {TULZU_PAT}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "claude-md-starters-sync",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())

    print(f"Committed to TulZu: {resp['commit']['sha'][:8]}")


def replace_sync_block(html: str, new_block: str) -> str:
    """Replace content between AUTO-SYNC START and AUTO-SYNC END markers."""
    pattern = re.compile(
        r"(// ── AUTO-SYNC START.*?// ── AUTO-SYNC END[^\n]*)",
        re.DOTALL
    )
    if not pattern.search(html):
        raise ValueError("AUTO-SYNC markers not found in claude-md-generator.html")
    return pattern.sub(new_block, html)


def main():
    if not TULZU_PAT:
        print("Error: TULZU_PAT not set — need PAT with write access to TulZu repo")
        raise SystemExit(1)

    print("Fetching latest templates from claude-md-starters...")

    # Map: JS key -> GitHub raw URL
    template_urls = {
        "'nextjs-app'":   f"{STARTERS_RAW}/nextjs/CLAUDE.md",
        "'react-vite'":   f"{STARTERS_RAW}/react-vite/CLAUDE.md",
    }

    # Pages Router template (optional — skip if not yet in repo)
    try:
        pages_content = fetch_raw(f"{STARTERS_RAW}/nextjs-pages/CLAUDE.md")
        template_urls["'nextjs-pages'"] = f"{STARTERS_RAW}/nextjs-pages/CLAUDE.md"
    except Exception:
        pages_content = None

    templates = {}
    for key, url in template_urls.items():
        try:
            templates[key.strip("'")] = fetch_raw(url)
            print(f"  Fetched: {key}")
        except Exception as e:
            print(f"  Skip {key}: {e}")

    if not templates:
        print("No templates fetched — aborting sync.")
        return

    # ADDONS stay hardcoded in the tool (they're not in the starters repo)
    # Read current ADDONS block from existing HTML and preserve it
    print("Fetching current TulZu HTML...")
    current_html, sha = get_tulzu_file()

    # Extract existing ADDONS block to preserve it
    addons_match = re.search(r"const ADDONS = \{(.*?)\};", current_html, re.DOTALL)
    addons_raw = addons_match.group(0) if addons_match else "const ADDONS = {};"

    # Build new BASE block
    base_lines = [
        SYNC_START,
        "// Source: github.com/sanjeevnair/claude-md-starters",
        "",
        "const BASE = {",
    ]
    for key, content in templates.items():
        escaped = escape_for_js_template(content.rstrip())
        base_lines.append(f"  '{key}': `{escaped}`,")
        base_lines.append("")
    base_lines.append("};")
    base_lines.append("")
    base_lines.append(addons_raw)
    base_lines.append("")
    base_lines.append(SYNC_END)

    new_block = "\n".join(base_lines)
    new_html = replace_sync_block(current_html, new_block)

    if new_html == current_html:
        print("No changes — TulZu already up to date.")
        return

    print("Pushing updated templates to TulZu repo...")
    put_tulzu_file(
        new_html,
        sha,
        "auto: sync CLAUDE.md templates from claude-md-starters\n\n"
        f"Updated templates: {', '.join(templates.keys())}"
    )
    print("Done — tulzu.com/tools/claude-md-generator updated.")


if __name__ == "__main__":
    main()
