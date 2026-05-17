# awesome-claude-md

> Production-ready `CLAUDE.md` templates for Claude Code — curated by [Sanjeev Nair](https://github.com/sanjeevnair).

A `CLAUDE.md` file is read by [Claude Code](https://claude.ai/code) at the start of every session. It tells Claude your stack, conventions, commands, and constraints — so you stop re-explaining them in every chat.

**A good CLAUDE.md cuts prompt overhead by 30–50% and dramatically improves first-attempt accuracy.**

---

## Quick start

Pick a template, copy it to your repo root, and fill in the `[placeholders]`.

```bash
# Clone and copy a template
curl -O https://raw.githubusercontent.com/sanjeevnair/awesome-claude-md/main/templates/nextjs/CLAUDE.md
```

Or use the **[interactive generator](https://www.tulzu.com/tools/claude-md-generator)** — pick your framework and stack options, get a ready-to-use file in 30 seconds.

---

## Templates

| Template | Framework | Description |
|----------|-----------|-------------|
| [`nextjs/`](templates/nextjs/CLAUDE.md) | Next.js 15 App Router | TypeScript, Tailwind, Prisma, shadcn/ui |
| [`react-vite/`](templates/react-vite/CLAUDE.md) | React 19 + Vite 5 | TypeScript, Tailwind, React Router, TanStack Query |
| [`_blank/`](templates/_blank/CLAUDE.md) | Any | Blank template with all sections |

More coming: Django, FastAPI, Go, Laravel, Ruby on Rails, SvelteKit.

---

## What makes a good CLAUDE.md?

### Include
- **Stack and versions** — Next.js 15, React 19, TypeScript strict, Tailwind v4
- **Commands** — dev, build, test, lint — exact commands, not descriptions
- **Folder structure** — what lives where and why
- **Code conventions** — naming, export style, file organisation
- **Key files** — which files control what behaviour
- **Do NOT list** — explicit anti-patterns for your codebase
- **Environment variables** — names and what they're for

### Avoid
- Restating general best practices Claude already knows
- Content that's easy to infer from reading the code
- Very long files (aim for 100–400 lines)

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

To add a new template:
1. Create `templates/[framework]/CLAUDE.md`
2. Follow the structure in `templates/_blank/CLAUDE.md`
3. Test it: open a real project with the template and verify Claude follows the conventions

---

## License

MIT
