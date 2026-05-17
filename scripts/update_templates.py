#!/usr/bin/env python3
"""
Fetch relevant CLAUDE.md examples from josix/awesome-claude-md,
filter for Next.js / React / Vite / Python / Rust projects, then use
Gemini 1.5 Flash (free tier) to suggest improvements to our starter
templates. Opens a PR if improvements are found.
"""

import os
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
GEMINI_MODEL    = "gemini-1.5-flash"

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
                            "content": content[:3000],
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
        for e in examples[:12]
    )
    templates_text = "\n\n---\n\n".join(
        f"## Our template: {name}\n\n{content}"
        for name, content in templates.items()
    )

    prompt = f"""You are reviewing real-world CLAUDE.md files from open-source projects. Your job is to improve our starter templates by incorporating patterns that appear consistently across multiple real projects.

## Real-world examples

{examples_text}

## Our current starter templates

{templates_text}

## Task

For each of our starter templates, suggest specific, concrete improvements based on patterns you see in the real-world examples. Only suggest changes that:
1. Appear in at least 2 of the real examples
2. Are genuinely useful — not padding or generic advice
3. Are specific to the framework/language (not obvious best practices)
4. Are not already covered in our template

Return your response as a JSON object where keys are template filenames (e.g. "nextjs/CLAUDE.md") and values are the COMPLETE updated template content (not a diff — the full file). Only include templates that actually need changes. If no improvements are needed, return an empty JSON object {{}}.

Return ONLY valid JSON with no markdown code fences."""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GOOGLE_API_KEY}"
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.2,
        }
    }).encode()

    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())

    text = resp["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip markdown fences if Gemini adds them
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3].rstrip()

    return json.loads(text.strip())

# ── Apply changes and open PR ─────────────────────────────────────────────────

def apply_and_pr(updates: dict[str, str]) -> None:
    if not updates:
        print("No improvements suggested. Templates are up to date.")
        return

    branch = "auto/template-improvements"
    subprocess.run(["git", "checkout", "-b", branch], check=True)

    changed = []
    for template_name, new_content in updates.items():
        path = TEMPLATES_DIR / template_name
        if not path.parent.exists():
            print(f"  Skip unknown path: {template_name}")
            continue
        path.write_text(new_content)
        changed.append(template_name)
        print(f"  Updated: {template_name}")

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
        "**Model used:** Gemini 1.5 Flash\n\n"
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
