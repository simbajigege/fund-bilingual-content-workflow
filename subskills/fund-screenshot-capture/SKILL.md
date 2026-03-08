---
name: fund-screenshot-capture
description: 根据基金代码访问 ai2alpha guru 页面并自动生成内容生产所需截图（全页、热力图区域、历史堆叠图区域、个股双轴图区域）的工具子技能。用于内容写作前的素材准备与截图占位替换。
---

# Fund Screenshot Capture

## Overview

输入基金代码，自动打开 `https://ai2alpha.cn/zh/guru/<fund_code>/` 并产出截图文件与清单。

## Use

```bash
python subskills/fund-screenshot-capture/scripts/capture_guru_screenshots.py \
  --fund-code 159730 \
  --output-dir ./content_output/159730/screenshots
```

## Output

- `full_page.png`
- `top_overview.png`
- `heatmap_region.png`
- `stacked_chart_region.png`
- `dual_axis_region.png`
- `manifest.json`

## Notes

- 该技能只负责截图，不参与选题或写作。
- 若页面结构变化导致局部截图失败，至少保留 `full_page.png`。
