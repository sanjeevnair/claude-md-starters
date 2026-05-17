#!/usr/bin/env python3
"""
Fetch relevant CLAUDE.md examples from josix/awesome-claude-md,
filter for Next.js / React / Vite / Python / Rust projects, then use
Gemini 2.5 Flash (free tier) to suggest improvements to our starter
templates. Opens a PR if improvements are found.
"""

import os
import re
import sys
import json
import base64
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

JOSIX_REPO    = "josix/awesome-claude-md"
JOSIX_SCENARIOS = "scenarios"
GOOGLE_API_KEY  = os.environ.get("GOOGLE_API_KEY", "")
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
GEMINI_MODEL    = "gemini-2.5-flash"

RELEVANT_KEYWORDS = [
    "next.js", "nextjs", "next js", "app router", "pages router",
    "react", "vite", "typescript", "tailwind", "shadcn",
    "vercel", "react router", "tanstack",
    "python", "fastapi", "django", "flask", "pydantic", "uvicorn",
    "rust", "cargo", "tokio", "clippy",
    "node.js", "nodejs", "express",
    "llm", "openai", "langchain", "anthropic", "embedding",
]

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# ── GitHub API ────────────────────────────────────────────────────────────────

def github_get(path: str) -> dict | list:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{path}",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "claude-md-starters-updater",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  GitHub API error {path}: {e}")
        return []


def file_content(path: str) -> str:
    data = github_get(f"{JOSIX_REPO}/contents/{path}")
    if isinstance(data, dict) and data.get("encoding") == "base64":
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    return ""


def list_dir(path: str) -> list[dict]:
    items = github_get(f"{JOSIX_REPO}/contents/{path}")
    return items if isinstance(items, list) else []

# ── Fetch relevant josix examples ─────────────────────────────────────────────

def is_relevant(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in RELEVANT_KEYWORDS)


def fetch_relevant_examples() -> list[dict]:
    relevant = []
    categories = [i for i in list_dir(JOSIX_SCENARIOS) if i["type"] == "dir"]

    for cat in categories:
        projects = [i for i in list_dir(f"{JOSIX_SCENARIOS}/{cat['name']}") if i["type"] == "dir"]
        for proj in projects:
            proj_path = f"{JOSIX_SCENARIOS}/{cat['name']}/{proj['name']}"
            files = list_dir(proj_path)
            for f in files:
                if f["name"].upper() in ("README.MD", "CLAUDE.MD"):
                    content = file_content(f"{proj_path}/{f['name']}")
                    if content and is_relevant(content):
                        relevant.append({
                            "project": proj["name"],
                            "file": f["name"],
                            "content": content[:1500],
                        })
                    break  # one file per project

    print(f"Found {len(relevant)} relevant examples")
    return relevant

# ── Read our templates ────────────────────────────────────────────────────────

def read_templates() -> dict[str, str]:
    return {
        str(p.relative_to(TEMPLATES_DIR)): p.read_text()
        for p in TEMPLATES_DIR.rglob("CLAUDE.md")
    }

# ── Call Gemini API ───────────────────────────────────────────────────────────

def ask_gemini(examples: list[dict], templates: dict[str, str]) -> dict[str, str]:
    examples_text = "\n\n---\n\n".join(
        f"## {e['project']} ({e['file']})\n\n{e['content']}"
        for e in examples[:5]  # keep prompt tight
    )

    # List template names and first 20 lines only — ask for additions, not full rewrites
    template_summaries = "\n\n".join(
        f"### {name}\n" + "\n".join(content.splitlines()[:20]) + "\n..."
        for name, content in templates.items()
    )

    prompt = f"""You are reviewing real-world CLAUDE.md files from open-source projects. Suggest improvements to starter templates based on patterns that appear in multiple real projects.

## Real-world examples (filtered for Next.js / React / TypeScript / Python / Rust)

{examples_text}

## Our starter templates (first 20 lines of each shown)

{template_summaries}

## Task

Return a JSON object where:
- keys = template filenames (e.g. "nextjs/CLAUDE.md")
- values = ONLY the new markdown sections to APPEND to that template (not the full file)

Rules:
1. Only suggest additions that appear in 2+ real examples
2. Be specific and terse — no generic advice
3. Skip anything already covered (visible in the first 20 lines)
4. If nothing to add, return {{}}

Example output format:
{{"nextjs/CLAUDE.md": "## Debugging\\n- Use VS Code debugger with Next.js config...", "react-vite/CLAUDE.md": "## Performance\\n- Use React DevTools Profiler..."}}"""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GOOGLE_API_KEY}"
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 4096,      # enough for section additions per template
            "temperature": 0.1,
            "responseMimeType": "application/json",  # force JSON mode
        }
    }).encode()

    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())

    # Check finish reason
    candidate = resp["candidates"][0]
    finish = candidate.get("finishReason", "")
    if finish not in ("STOP", ""):
        print(f"  Gemini finish reason: {finish} — skipping update")
        return {}

    text = candidate["content"]["parts"][0]["text"].strip()

    # Belt-and-braces fence strip even with responseMimeType set
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text.rstrip())

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        print(f"  Raw response (first 500 chars): {text[:500]}")
        return {}

# ── Apply changes and open PR ─────────────────────────────────────────────────

def apply_and_pr(updates: dict[str, str]) -> None:
    if not updates:
        print("No improvements suggested. Templates are up to date.")
        return

    branch = "auto/template-improvements"
    subprocess.run(["git", "checkout", "-b", branch], check=True)

    changed = []
    for template_name, additions in updates.items():
        path = TEMPLATES_DIR / template_name
        if not path.exists():
            print(f"  Skip unknown template: {template_name}")
            continue
        if not additions.strip():
            continue
        # APPEND new sections to existing template
        existing = path.read_text()
        path.write_text(existing.rstrip() + "\n\n" + additions.strip() + "\n")
        changed.append(template_name)
        print(f"  Appended to: {template_name}")

    if not changed:
        print("No valid templates updated.")
        return

    subprocess.run(
        ["git", "add"] + [str(TEMPLATES_DIR / c) for c in changed],
        check=True
    )
    subprocess.run(
        ["git", "commit", "-m",
         f"auto: improve templates from josix/awesome-claude-md examples\n\nUpdated: {', '.join(changed)}"],
        check=True
    )
    subprocess.run(["git", "push", "origin", branch], check=True)

    body = (
        "## Automated template improvements\n\n"
        "Opened by the weekly update action. Changes based on patterns found in "
        "relevant projects in [josix/awesome-claude-md](https://github.com/josix/awesome-claude-md).\n\n"
        f"**Updated:** {', '.join(changed)}\n\n"
        "**Model used:** Gemini 2.5 Flash\n\n"
        "Please review before merging."
    )

    subprocess.run([
        "gh", "pr", "create",
        "--title", "auto: weekly template improvements from real-world examples",
        "--body", body,
        "--base", "main",
        "--head", branch,
    ], check=True)

    print(f"PR opened for: {changed}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not set")
        sys.exit(1)

    print("Fetching relevant examples from josix/awesome-claude-md...")
    examples = fetch_relevant_examples()

    if not examples:
        print("No relevant examples found this run. Exiting.")
        return

    print("Reading current templates...")
    templates = read_templates()

    print("Asking Gemini for improvement suggestions...")
    updates = ask_gemini(examples, templates)

    print(f"Suggested updates for: {list(updates.keys()) or 'none'}")
    apply_and_pr(updates)


if __name__ == "__main__":
    main()
