# Contributing

Thanks for helping improve this collection of skills.

## Adding a Skill

1. Create a folder under `skills/` named after the skill (lowercase, hyphen-separated, e.g. `latex-review`).
2. Write a `SKILL.md` with YAML frontmatter:
   - `name`: the skill name, matching the folder name.
   - `description`: a one-line description of the capability, including common trigger keywords. Agents rely on it to decide when to load the skill.
3. Optionally add `references/` (detailed docs), `scripts/` (scripts), or `template/` (templates).
4. If third-party code or licenses are involved, place a `LICENSE.txt` inside the skill directory.
5. Update the skills table in the root `README.md`.

## Checklist

- [ ] The `description` in `SKILL.md` lets an agent reliably decide when to trigger the skill
- [ ] The body is concise; details are split into `references/`
- [ ] Scripts have clear usage instructions and no undeclared environment dependencies
- [ ] No secrets or personal paths included

## Commits

Follow the [Conventional Commits](https://www.conventionalcommits.org) format:

```
<type>: <short description in present tense>
```

Common types: `feat` (new skill or capability), `fix`, `docs`, `refactor`, `chore`. Scope the change by name when useful, e.g. `feat: add deep-summary skill`.
