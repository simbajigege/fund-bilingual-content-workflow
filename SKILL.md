---
name: fund-bilingual-content-workflow
description: 投资大师/基金持仓分析的主流程编排技能。用于输入基金代码后，先调用数据解读子技能完成热力图/堆叠图/双轴分析，再把上下文交给选题策划、调研深化、博客写作、双语输出四个LLM子技能逐段直接产出内容。主技能只负责编排与统一方法，不硬编码写文。
---

# Fund Bilingual Content Workflow

## Overview

输入一个基金代码，先完成数据解读与上下文打包，再由4个内容子 skill 按顺序由模型直接输出内容。
优先使用 `scripts/run_main_workflow.py` 一键准备上下文。

## Integrated Subskills

本技能在 `subskills/` 内直接集成以下三个子 skill（不独立存在于主 skill 外）：

- `fund-heatmap-analysis`
- `fund-historical-positions-analysis`
- `fund-dual-axis-analysis`
- `fund-topic-planning`
- `fund-research-deepening`
- `fund-blog-writing`
- `fund-bilingual-output`
- `fund-screenshot-capture`

默认调用路径（相对当前 skill 目录）：

- `subskills/fund-heatmap-analysis/scripts/fetch_and_analyze.py`
- `subskills/fund-historical-positions-analysis/scripts/quick_analysis.py`
- `subskills/fund-dual-axis-analysis/scripts/fetch_and_analyze.py`
- `subskills/fund-topic-planning/SKILL.md`
- `subskills/fund-research-deepening/SKILL.md`
- `subskills/fund-blog-writing/SKILL.md`
- `subskills/fund-bilingual-output/SKILL.md`
- `subskills/fund-screenshot-capture/SKILL.md`

## Quick Start

在仓库根目录执行：

```bash
python fund-bilingual-content-workflow/scripts/run_main_workflow.py \
  --fund-code 159730 \
  --quarters 12 \
  --capture-screenshots \
  --output-dir ./content_output
```

输出目录结构：

```text
content_output/
  159730/
    analysis/
      heatmap/
      historical/
      dual_axis/
    screenshots/
      full_page.png
      heatmap_region.png
      stacked_chart_region.png
      dual_axis_region.png
      manifest.json
    workflow_context.json
```

## Workflow

1. 运行三类数据解读子 skill，生成结构化分析结果。
2. 汇总为 `workflow_context.json`，作为内容阶段统一输入。
3. 用 `fund-topic-planning`（LLM直出）产出选题矩阵。
4. 用 `fund-research-deepening`（LLM直出）产出研究包。
5. 用 `fund-blog-writing`（LLM直出）产出中文长文草稿（含截图占位）。
6. 用 `fund-bilingual-output`（LLM直出）产出中英文成稿。
7. 用 `fund-screenshot-capture`（工具子skill）生成真实截图并在正文中替换占位。

## Content Rules

- 每篇必须包含：
- 反常识开头钩子
- 至少 3 个数据点
- 三类截图占位中的至少 2 类
- 13F 披露延迟（约 45 天）提示
- 非投资建议声明
- 工具跳转 CTA

截图占位格式：

```text
--- 📸 [工具截图 · 持仓热力图 · <基金代码> · <季度>] 
图注：色块大小=仓位权重，颜色=AI评级
→ 查看实时数据：[工具链接]
---
```

## Parameters

- `--fund-code` 必填，基金代码
- `--quarters` 默认 `12`
- `--top-n` 默认 `8`，双轴分析关注股票数
- `--skip-analysis` 仅基于已有 analysis 文件重新打包上下文
- `--capture-screenshots` 启用页面截图采集（ai2alpha guru 页面）

## References

- 详细规则：`references/workflow-rules.md`
- 风格参考说明：`references/style-reference-note.md`

## Notes

- 主脚本不直接生成选题/调研/文章文案，避免硬编码产出。
- 内容产出由4个LLM子 skill 在足够上下文下直接完成。
