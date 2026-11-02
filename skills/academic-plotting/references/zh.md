# 中文速查（plotkit）

本 skill 是**个人学术绘图风格** + **可运行例子库**，不绑定任何具体项目。
细节以英文参考文件为准，这里给出定位、规则与速查表。

## 三步上手

1. 先看 [recipes/index.md](../recipes/index.md)，挑最接近的一张图，读对应
   `recipe.md` 与 `plot.py`，只换数据、保留布局调用。
2. 没有对应图型时查 [api-index.md](./api-index.md)（每个函数一行签名）。
3. 需要细节再读对应英文 reference；不要在脚本里复制样式代码或手写 `***` 判断。

## 安装

```bash
python scripts/install_plotkit.py --project /path/to/project --mode copy
python scripts/install_plotkit.py --project /path/to/project --check
```

`--mode link` 指向本 skill 的副本（单一来源，改库即生效）；`--mode copy` 复制一份
（适合投稿前冻结版本）。未安装时，把本 skill 的 `scripts/` 加入 `sys.path` 即可。

## 样式三选

```python
from plotkit import use_style

use_style("print")          # 8pt，按最终印刷宽度 → 投稿用（推荐）
use_style("base")           # 12pt，屏幕/组会的大字风格
use_style("presentation")   # 16pt，粗线 → 汇报
```

字体栈 Arial → Helvetica → Liberation Sans → DejaVu Sans；缺 Arial 时会告警并
给出实际使用的字体，避免换机器后图变样。

## 硬规则

- 先 `use_style()`，再创建 figure；一张图只用一种样式。
- 颜色走**语义角色**：`condition("control")`、`categorical(n)`、
  `shades(hue, n)`；图里不出现裸 hex。项目色用 `register_palette` /
  `register_family` 注册。
- 显著性走 `p_to_stars` / `add_sig_bar` / `annotate_test`；需要精确 p 值时用
  `exact=True`。
- 均值必须带不确定性（误差带或误差棒）；图例 `frameon=False`，图例 marker 与
  数据点同尺寸。
- 抖动用 `seed` 参数，保证两次渲染结果一致。
- 交付矢量图；大批量数据层（热图/图像）加 `rasterized=True`。

## API 速查

### 画布与版式

| 函数 | 用途 |
|---|---|
| `new_axes("single")` / `mm(89, 67)` | 单图，预设或期刊毫米尺寸 |
| `panel_grid(1, 3, width="double")` | 多面板，自动按宽高比定图高 |
| `panel_labels(axes)` | (a)(b)(c) 面板编号 |
| `shared_limits(axes)` | 多面板统一坐标范围 |

### 颜色

| 函数 | 用途 |
|---|---|
| `condition("control" / "treatment")` | 对照组 / 实验组 |
| `categorical(n)` | n 个分类色 |
| `shades(hue, n)` | 同一色相的明暗梯度（4 条曲线仍可读） |
| `register_palette(name, {...})` | 注册项目色表 |
| `diverging_cmap()` / `sequential_cmap(hue)` | 发散 / 单色相连续色图 |

### 统计与标注

| 函数 | 用途 |
|---|---|
| `compare(a, b, test="auto")` | 配对 t / Welch / Wilcoxon / Mann-Whitney |
| `compare(...).label(exact=True)` | 星号或 `p = 0.03` |
| `anova([g1, g2, g3])` / `adjust(pvals)` | 多组检验 + Holm 校正 |
| `annotate_test(ax, x1, x2, a, b)` | 检验 + 标注一步完成 |
| `add_sig_bar` / `add_bracket` | 显著性横杠 / 分组括号（按 y 轴量程自动缩放） |

### 图型

| 函数 | 用途 |
|---|---|
| `multi_raincloud([(pre, post), ...])` | 配对雨云图（含个体连线） |
| `box_with_jitter(ax, groups)` | 箱线 + 抖动散点 |
| `line_with_band(ax, x, y, yerr=sem)` | 均值折线 + 误差带 |
| `bar_with_error(ax, groups, vals, yerr=...)` | 柱状 + 误差棒 |
| `grouped_bars(ax, groups, {...}, yerr={...})` | 分组柱状 |
| `rounded_heatmap(ax, data, cmap, norm, ...)` | 圆角单元格热图（可加行列标签与色条） |
| `radar_chart(ax, dims, {...})` | 六边形雷达（r_max 自动） |
| `plot_family_curves(ax, x, data, family)` | 家族曲线（一族一色相） |
| `scatter_with_fit(ax, xs, ys, color)` | 散点 + 回归 + 95% CI |

### 保存

```python
from plotkit import save_fig

save_fig(fig, "fig1c", out_dir="assets/fig1", formats=("svg", "png"), close=True)
```

返回 `{"svg": path, "png": path}`。`pdf.fonttype=42` 已设为默认（可编辑文字，
期刊可接受）；`svg_text=True` 保留 SVG 文字而非转曲。

## 例子库

| 例子 | 场景 |
|---|---|
| [01-paired-raincloud](../recipes/01-paired-raincloud/recipe.md) | 配对前后对比，含个体连线与显著性 |
| [02-family-curves](../recipes/02-family-curves/recipe.md) | 参数扫描 / 鲁棒性曲线，多系列 |
| [03-rounded-heatmap](../recipes/03-rounded-heatmap/recipe.md) | 评分矩阵、被试×条目 |
| [04-radar-and-box](../recipes/04-radar-and-box/recipe.md) | 多维剖面 + 分组分布 |
| [05-errorband-and-panels](../recipes/05-errorband-and-panels/recipe.md) | 三面板：误差带、柱+误差、拟合+色条 |

## 新增一个例子

1. 建目录 `recipes/<NN-slug>/`，放 `plot.py`（`main(out_dir)` + `--out`）与
   `recipe.md`（frontmatter 必填 `title`、`intent`、`data_shape`、`functions`）。
2. 运行 `python recipes/<NN-slug>/plot.py` 查看效果（默认输出到临时目录，生成的图不进 skill 目录）。
3. `python scripts/list_recipes.py` 重建索引。
4. 两次运行对比 PNG，确认可复现。

## 排错

| 现象 | 处理 |
|---|---|
| `ModuleNotFoundError: plotkit` | 安装，或把 `scripts/` 加入 `sys.path` |
| 统计函数报缺 scipy | `pip install scipy`（库本身不强制依赖） |
| 字体告警 | 装 Arial / Liberation Sans，或接受告警中给出的替代字体 |
| 中文变方块 | 注册中文字体并加入 `font.sans-serif` 首位 |
| 负号变方块 | 所有样式已设 `axes.unicode_minus=False` |
| 两次出图不一致 | 检查自己的 `np.random.seed`，两次渲染对比 PNG |
| 热图/内嵌色条触发布局告警 | 改用 `add_colorbar(fig, mappable, ax=ax)` |
