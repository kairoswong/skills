# skills

个人 AI Agent Skills 集合。每个 skill 是一个包含指令、脚本和资源的文件夹，AI Agent 可以自动发现并使用它们来完成特定任务——写一次，到处用。

English version: [README.md](README.md)

## 什么是 Skill？

Skill 是一个包含 `SKILL.md` 的文件夹，`SKILL.md` 中用 Markdown 描述该能力的工作流程、约束和资源。Agent 在执行任务时会根据描述自动加载匹配的 skill，并按需读取其中的参考文档（`references/`）或执行脚本（`scripts/`）。

一个典型的 skill 目录结构：

```
skills/<skill-name>/
├── SKILL.md          # 必需：入口文件，描述能力与工作流程
├── references/       # 可选：按需加载的详细文档
├── scripts/          # 可选：可执行脚本
└── LICENSE.txt       # 可选：单个 skill 的许可证
```

## 当前包含的 Skills


| Skill      | 说明     |
| ------------ | ---------- |
| [academic-plotting](skills/academic-plotting/SKILL.md) | 个人论文配图的 matplotlib 风格，附可直接运行的示例 |
| [deep-summary](skills/deep-summary/SKILL.md) | 把一段文本总结成一篇有深度、有批判性的文章——重构论点、拆解论证并给出评述，而非要点罗列 |
| [photo-reel](skills/photo-reel/SKILL.md) | 把照片文件夹和音乐渲染成卡点竖屏照片视频（Python/Pillow + ffmpeg） |

## 目录约定

- `skills/` — 纳入版本管理的 skills，每个子文件夹一个 skill。

## 安装与使用

推荐通过 [`skills` CLI](https://skills.sh)（Vercel Labs 出品）安装。它会将 skill 装入 OpenCode、Claude Code、Codex 等 70+ 个 Agent，自动探测本机已安装的 Agent 并放入对应目录：

```bash
npx skills add <owner>/skills --skill deep-summary --yes
npx skills update    # 之后拉取最新版本
```

也可以手动把 skill 文件夹复制到 Agent 的 skills 目录（OpenCode：`~/.config/opencode/skills/`；其他工具路径以其文档为准）。

安装后重启 Agent，即可在对话中通过任务描述自动触发，或直接按名称调用。

## 编写 Skill 的建议

1. **`SKILL.md` 的 frontmatter** 写清 `name` 和 `description`：`description` 决定了 Agent 何时触发这个 skill，应包含触发关键词。
2. **正文保持精炼**：只写 Agent 必须遵守的流程和约束；细节内容拆到 `references/` 中按需加载。
3. **脚本是可选加速项**：把确定性强的操作写成脚本放在 `scripts/`，让 Agent 调用而不是临场发挥。
4. **一个 skill 只做一件事**：能力边界清晰才容易被正确触发。
