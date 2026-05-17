# Contributing to awesome-claude-md

## Adding a new template

1. Fork the repo
2. Create `templates/[framework]/CLAUDE.md`
3. Use `templates/_blank/CLAUDE.md` as your starting point
4. Include all standard sections (see README)
5. Test it: open a real project with the template and verify Claude follows the conventions
6. Submit a PR with a brief description of the framework and what makes the template useful

## Improving an existing template

- Fix inaccuracies (outdated commands, wrong file paths)
- Add missing conventions that are common in that ecosystem
- Add `Do NOT` rules based on real mistakes Claude makes without them

## Template quality bar

A template should pass this test: *"If I dropped this CLAUDE.md into a fresh project, would Claude Code produce idiomatic, convention-following code from the first message?"*

If yes — it's ready.
