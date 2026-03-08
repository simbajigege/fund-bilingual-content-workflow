---
name: fund-blog-writing
description: 基于选题与调研包执行“博客写作（含工具截图引用）”的LLM子技能。用于生成7段式中文长文草稿，嵌入热力图/堆叠图/双轴图截图占位与图注，强调数据证据链与风险边界。此技能要求模型直接写作，不通过脚本硬编码产出文章。
---

# Fund Blog Writing

## Overview

按7段式结构完成中文文章初稿，要求“工具截图=证据，不是装饰”。

## Inputs

- 单个选题
- 对应 Research Packet
- 工具链接与截图占位规范

## Required Structure

1. 开篇钩子（反常识 + 数字）
2. 工具全景解读（热力图 + 堆叠图）
3. 历史数据呈现（表格/时间轴）
4. 表象背后机制（核心叙事）
5. 大师评价 + 持仓行为双验证
6. 风险提示（边界条件）
7. 行动建议（可执行框架）

## Screenshot Rule

每篇至少2-3张占位，优先顺序：
- 热力图（开场）
- 堆叠图（稳定性/是否可跟踪）
- 双轴图（单股收益轨迹）

若主流程提供了 `screenshot_context`，优先使用其中真实文件路径替换占位：
- `heatmap_region.png`
- `stacked_chart_region.png`
- `dual_axis_region.png`

## Output Format

输出 Markdown：
- 带标题、7段正文、截图占位、图注、CTA链接
- 含“13F约45天延迟”和“不构成投资建议”

## Constraints

- 每个核心结论至少一个数据锚点。
- 不能写成纯广告，必须包含风险与反例。
