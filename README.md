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
| [academic-plotting](skills/academic-plotting/SKILL.md) | Personal matplotlib style for paper and thesis figures, with runnable example recipes |
| [deep-summary](skills/deep-summary/SKILL.md) | Turn a piece of text into one in-depth, critical article — thesis reconstruction, argument tracing, and commentary, not a bullet digest |
| [photo-reel](skills/photo-reel/SKILL.md) | Render photos + music into a beat-synced vertical photo-reel video with Python/Pillow + ffmpeg |

## Repository Layout

- `skills/` — versioned skills, one subfolder per skill.

## Installing a Skill

The recommended way is the [`skills` CLI](https://skills.sh) (by Vercel Labs), which installs skills into OpenCode, Claude Code, Codex, and 70+ other agents — one copy, detected and linked into every installed agent:

```bash
npx skills add <owner>/skills --skill deep-summary --yes
npx skills update    # pull the latest versions later
```

Alternatively, copy the skill folder you need into your agent's skills directory manually (OpenCode: `~/.config/opencode/skills/`; other tools vary — consult their documentation).

Restart your agent after installing. The skill will then be triggered automatically by task descriptions, or can be invoked by name.

## Writing a Skill

1. **Frontmatter of `SKILL.md`**: set `name` and `description` clearly — the `description` determines when the agent triggers the skill, so include common trigger keywords.
2. **Keep the body concise**: only include the workflow and constraints the agent must follow; move details into `references/` to be loaded on demand.
3. **Scripts are optional accelerators**: encode deterministic operations as scripts in `scripts/` and have the agent invoke them instead of improvising.
4. **One skill, one job**: a clearly bounded capability is far more likely to be triggered correctly.
