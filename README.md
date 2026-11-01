# skills

A collection of personal Agent Skills — folders of instructions, scripts, and resources that AI agents can discover and use to perform specific tasks. Write once, use everywhere.

中文说明：[README.zh.md](README.zh.md)

## What is a Skill?

A skill is a folder containing a `SKILL.md` file that describes, in Markdown, the workflow, constraints, and resources for a capability. Agents automatically load matching skills based on the task at hand, then read the reference docs (`references/`) or run the scripts (`scripts/`) as needed.

A typical skill layout:

```
skills/<skill-name>/
├── SKILL.md          # Required: entry point describing the capability and workflow
├── references/       # Optional: detailed docs loaded on demand
├── scripts/          # Optional: executable scripts
└── LICENSE.txt       # Optional: per-skill license
```

## Included Skills


| Skill         | Description |
| --------------- | ------------- |
| [deep-summary](skills/deep-summary/SKILL.md) | Turn a piece of text into one in-depth, critical article — thesis reconstruction, argument tracing, and commentary, not a bullet digest |

## Repository Layout

- `skills/` — versioned skills, one subfolder per skill.
- Other folders at the repository root (e.g. `academic-plotting/`, `story2film/`) are skills under local development; they are excluded via `.gitignore` and will be moved into `skills/` once finalized.

## Installing a Skill

Copy or clone the skill folder you need into your agent's skills directory. The location varies by tool — consult your tool's documentation (for example, OpenCode typically uses `~/.config/opencode/skills/`).

Restart your agent after installing. The skill will then be triggered automatically by task descriptions, or can be invoked by name.

## Writing a Skill

1. **Frontmatter of `SKILL.md`**: set `name` and `description` clearly — the `description` determines when the agent triggers the skill, so include common trigger keywords.
2. **Keep the body concise**: only include the workflow and constraints the agent must follow; move details into `references/` to be loaded on demand.
3. **Scripts are optional accelerators**: encode deterministic operations as scripts in `scripts/` and have the agent invoke them instead of improvising.
4. **One skill, one job**: a clearly bounded capability is far more likely to be triggered correctly.
