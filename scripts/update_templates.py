#!/usr/bin/env python3
"""
Fetch relevant CLAUDE.md examples from josix/awesome-claude-md,
filter for Next.js / React / Vite projects, then use Claude API
to suggest improvements to our starter templates.
Opens a PR if improvements are found.
"""

import os
import sys
import json
import base64
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

JOSIX_REPO = "josix/awesome-claude-md"
JOSIX_SCENARIOS_PATH = "scenarios"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Keywords that signal a Next.js / React / TypeScript / Vite project
RELEVANT_KEYWORDS = [
    "next.js", "nextjs", "next ", "app router", "pages router",
    "react", "vite", "typescript", "tailwind", "shadcn",
    "vercel", "react router", "remix", "gatsby", "tanstack",
]

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# ── GitHub API helpers ─────────────────────────────────────────────────────────

def github_get(path: str) -> dict | list:
    url = f"https://api.github.com/repos/{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "claude-md-starters-updater",
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def get_file_content(repo: str, file_path: str) -> str | None:
    try:
        data = github_get(f"{repo}/contents/{file_path}")
        if isinstance(data, dict) and data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except Exception:
        return None


def list_dir(repo: str, path: str) -> list[dict]:
    try:
        items = github_get(f"{repo}/contents/{path}")
        return items if isinstance(items, list) else []
    except Exception:
        return []

# ── Fetch josix examples ───────────────────────────────────────────────────────

def is_relevant(content: str) -> bool:
    lower = content.lower()
    return any(kw in lower for kw in RELEVANT_KEYWORDS)


def fetch_relevant_examples() -> list[dict]:
    """Walk josix scenarios, return CLAUDE.md files relevant to our frameworks."""
    relevant = []
    categories = list_dir(JOSIX_REPO, JOSIX_SCENARIOS_PATH)

    for cat in categories:
        if cat["type"] != "dir":
            continue
        projects = list_dir(JOSIX_REPO, f"{JOSIX_SCENARIOS_PATH}/{cat['name']}")
        for proj in projects:
            if proj["type"] != "dir":
                continue
            # Check project README or CLAUDE.md
            proj_path = f"{JOSIX_SCENARIOS_PATH}/{cat['name']}/{proj['name']}"
            files = list_dir(JOSIX_REPO, proj_path)
            for f in files:
                if f["name"].upper() in ("CLAUDE.MD", "README.MD"):
                    content = get_file_content(JOSIX_REPO, f"{proj_path}/{f['name']}")
                    if content and is_relevant(content):
                        relevant.append({
                            "project": proj["name"],
                            "file": f["name"],
                            "content": content[:3000],  # cap per file
                        })
                        break  # one file per project is enough

    print(f"Found {len(relevant)} relevant examples from josix")
    return relevant

# ── Read our current templates ─────────────────────────────────────────────────

def read_templates() -> dict[str, str]:
    templates = {}
    for path in TEMPLATES_DIR.rglob("CLAUDE.md"):
        name = str(path.relative_to(TEMPLATES_DIR))
        templates[name] = path.read_text()
    return templates

# ── Call Claude API ────────────────────────────────────────────────────────────

def ask_claude(examples: list[dict], templates: dict[str, str]) -> dict[str, str]:
    """Ask Claude to suggest improvements to our templates based on real examples."""

    examples_text = "\n\n---\n\n".join(
        f"## {e['project']} ({e['file']})\n\n{e['content']}"
        for e in examples[:12]  # cap at 12 examples to stay within token budget
    )

    templates_text = "\n\n---\n\n".join(
        f"## Our template: {name}\n\n{content}"
        for name, content in templates.items()
    )

    prompt = f"""You are reviewing real-world CLAUDE.md files from open-source projects that use Next.js, React, TypeScript, or Vite. Your job is to improve our starter templates by incorporating patterns that appear consistently across multiple real projects.

## Real-world examples from josix/awesome-claude-md

{examples_text}

## Our current starter templates

{templates_text}

## Task

For each of our starter templates, suggest specific, concrete improvements based on patterns you see in the real-world examples. Only suggest changes that:
1. Appear in at least 2 of the real examples
2. Are genuinely useful (not just padding)
3. Are specific to the framework (not generic advice)
4. Are not already covered in our template

Return your response as a JSON object where keys are template filenames (e.g. "nextjs/CLAUDE.md") and values are the COMPLETE updated template content (not a diff — the full file). Only include templates that need changes. If no improvements are needed, return an empty object {{}}.

Return ONLY valid JSON, no markdown fences."""

    payload = json.dumps({
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    )

    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())

    text = resp["content"][0]["text"].strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
        if text.endswith("```"):
            text = text[:-3]

    return json.loads(text.strip())

# ── Apply changes and open PR ──────────────────────────────────────────────────

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
            print(f"Skip unknown template path: {template_name}")
            continue
        path.write_text(new_content)
        changed.append(template_name)
        print(f"Updated: {template_name}")

    if not changed:
        print("No valid template paths updated.")
        return

    subprocess.run(["git", "add"] + [str(TEMPLATES_DIR / c) for c in changed], check=True)
    subprocess.run(["git", "commit", "-m",
        f"auto: improve templates from josix/awesome-claude-md examples\n\nUpdated: {', '.join(changed)}"],
        check=True
    )
    subprocess.run(["git", "push", "origin", branch], check=True)

    body = (
        "## Automated template improvements\n\n"
        "This PR was opened by the weekly update action. Changes are based on patterns "
        "found in relevant Next.js/React/TypeScript projects in "
        "[josix/awesome-claude-md](https://github.com/josix/awesome-claude-md).\n\n"
        f"**Templates updated:** {', '.join(changed)}\n\n"
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

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print("Fetching relevant examples from josix/awesome-claude-md...")
    examples = fetch_relevant_examples()

    if not examples:
        print("No relevant examples found this run. Exiting.")
        return

    print("Reading current templates...")
    templates = read_templates()

    print("Asking Claude for improvement suggestions...")
    updates = ask_claude(examples, templates)

    print(f"Suggested updates for: {list(updates.keys()) or 'none'}")
    apply_and_pr(updates)


if __name__ == "__main__":
    main()
