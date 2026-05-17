# claude-md-starters

> Opinionated `CLAUDE.md` starter templates for Claude Code — curated by [Sanjeev Nair](https://github.com/sanjeevnair).

A `CLAUDE.md` file is read by [Claude Code](https://claude.ai/code) at the start of every session. It tells Claude your stack, conventions, commands, and constraints — so you stop re-explaining them in every chat.

**A good CLAUDE.md cuts prompt overhead by 30–50% and improves first-attempt accuracy.**

> **These are starters** — opinionated, copy-paste-ready templates for specific frameworks. Fill in the `[placeholders]` and drop the file in your repo root.
>
> Looking for real-world examples from open-source projects? See [josix/awesome-claude-md](https://github.com/josix/awesome-claude-md) — a curated collection of CLAUDE.md files from leading OSS repos.

---

## Quick start

**Option 1 — Interactive generator (recommended)**

Use the **[Tulzu CLAUDE.md Generator](https://www.tulzu.com/tools/claude-md-generator)** — pick your framework and stack options, get a ready file in 30 seconds.

**Option 2 — Copy a template directly**

```bash
# Next.js App Router
curl -O https://raw.githubusercontent.com/sanjeevnair/claude-md-starters/main/templates/nextjs/CLAUDE.md

# React + Vite
curl -O https://raw.githubusercontent.com/sanjeevnair/claude-md-starters/main/templates/react-vite/CLAUDE.md

# Blank template
curl -O https://raw.githubusercontent.com/sanjeevnair/claude-md-starters/main/templates/_blank/CLAUDE.md
```

**Option 3 — Fork this repo**

Fork and customise the templates for your team's conventions. PRs welcome.

---

## Templates

| Template | Framework | Covers |
|----------|-----------|--------|
| [`nextjs/`](templates/nextjs/CLAUDE.md) | Next.js 15 App Router | TypeScript, Tailwind, Prisma, shadcn/ui, testing, env vars |
| [`react-vite/`](templates/react-vite/CLAUDE.md) | React 19 + Vite 5 | TypeScript, Tailwind, React Router, TanStack Query, Zustand |
| [`_blank/`](templates/_blank/CLAUDE.md) | Any | Blank template with all standard sections |

**More coming:** Django, FastAPI, Go, Laravel, SvelteKit, Ruby on Rails, Express.

---

## What a starter includes

Each template covers:

- **Stack and versions** — exact framework, language, libraries
- **Commands** — dev, build, test, lint — ready to copy
- **Folder structure** — what lives where and why
- **Code conventions** — naming, export style, file organisation
- **Key files** — which files control which behaviour
- **Do NOT list** — explicit anti-patterns Claude should avoid
- **Environment variables** — names, purpose, public vs private

---

## Suggest a template

Missing a framework? Open an [issue](https://github.com/sanjeevnair/claude-md-starters/issues/new?template=suggest-template.md&title=Template+request:+%5BFramework%5D) and describe your stack. Upvote existing requests to help prioritise.

Have a CLAUDE.md that works well for your team? Share it via PR — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## See also

- [josix/awesome-claude-md](https://github.com/josix/awesome-claude-md) — curated real-world CLAUDE.md examples from open-source projects (308 ⭐)
- [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code) — official Claude Code documentation
- [Tulzu CLAUDE.md Generator](https://www.tulzu.com/tools/claude-md-generator) — interactive starter generator

---

## License

MIT
