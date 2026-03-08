---
name: fund-heatmap-analysis
description: "基金持仓热力图数据分析技能，用于解析基金持仓数据并生成投资分析报告。当用户需要分析基金持仓热力图数据、提取关键信号、生成结构化分析报告或自然语言总结时使用此技能。支持通过基金代码自动调用API获取数据，或直接分析提供的JSON数据。"
---

# 基金持仓热力图数据分析技能

本技能用于分析基金持仓热力图数据，提取关键投资信号，生成结构化分析报告和自然语言总结，支持后续投资大师持仓分析内容生产工作流。

## 核心功能

1. **数据获取**：支持通过基金代码自动调用API获取实时持仓数据
2. **数据分析**：解析持仓数据，识别关键信号（大/小色块+红/绿色组合等）
3. **报告生成**：生成结构化JSON报告和自然语言分析总结
4. **工作流支持**：为投资博客内容生产提供数据支持

## 快速开始

### 方式一：通过基金代码分析

```bash
# 使用脚本获取并分析数据
python scripts/fetch_and_analyze.py --fund-code 159730 --output report.json
```

### 方式二：分析已有JSON数据

```bash
# 分析已获取的JSON数据
python scripts/analyze_data.py --input data.json --output analysis.json
```

## 数据字段说明

参见 [references/data_fields.md](references/data_fields.md) 了解完整的API返回字段说明。

## 分析逻辑

### 1. 热力图信号识别

基于`portfolio_weight_pct`（权重百分比）和`ai_rating`（AI评级）的组合分析：

| 信号类型 | 条件 | 解读 |
|---------|------|------|
| 大色块+绿色 | 权重 > 5% 且 ai_rating ∈ ["Strong Buy", "Buy"] | 大师重仓且AI看好 → 最强信号，值得重点分析 |
| 大色块+红色 | 权重 > 5% 且 ai_rating ∈ ["Sell", "Strong Sell"] | 大师重仓但AI看空 → 分歧点，最有故事性 |
| 小色块+绿色 | 权重 < 2% 且 ai_rating ∈ ["Strong Buy", "Buy"] | 轻仓潜力股 → 大师是否在悄悄建仓？ |
| 整体颜色偏红 | 持仓中"Sell"和"Strong Sell"评级占比 > 30% | 该大师当前持仓整体估值偏高，入场需谨慎 |

### 2. 财务指标分析

- **估值分析**：PE ratio、PB ratio分位数分析
- **价格动量**：change_pct、amplitude分析
- **流动性**：volume、turnover_rate分析
- **行业分布**：industry分类统计

### 3. AI投资建议分析

- `action`字段统计：持有/买入/卖出比例
- `confidence`置信度分析
- `target_price`目标价与当前价差距
- `risk_score`风险评估

## 输出结构

### 结构化JSON报告

报告包含以下部分：

```json
{
  "metadata": {
    "fund_code": "159730",
    "analysis_date": "2026-03-07",
    "total_stocks": 10,
    "total_market_value": 123456789
  },
  "heatmap_signals": {
    "strong_buy_heavy": [...],
    "strong_sell_heavy": [...],
    "strong_buy_light": [...],
    "overall_red_signal": false
  },
  "financial_analysis": {
    "valuation_summary": {...},
    "momentum_summary": {...},
    "liquidity_summary": {...}
  },
  "ai_advice_summary": {
    "action_distribution": {...},
    "confidence_stats": {...},
    "price_gap_stats": {...}
  },
  "industry_distribution": {...},
  "top_signals": [...]
}
```

### 自然语言分析总结

生成中文分析文本，包含：
- 持仓概况总结
- 关键信号发现
- 投资建议要点
- 风险提示

## 脚本说明

### scripts/fetch_data.py

获取基金持仓数据：

```bash
python scripts/fetch_data.py --fund-code 159730 --output data.json
```

参数：
- `--fund-code`: 基金代码（必需）
- `--output`: 输出文件路径（可选，默认：fund_data.json）

### scripts/analyze_data.py

分析持仓数据：

```bash
python scripts/analyze_data.py --input data.json --output analysis.json --summary-text summary.txt
```

参数：
- `--input`: 输入JSON文件路径（必需）
- `--output`: 结构化分析报告输出路径（可选）
- `--summary-text`: 自然语言总结输出路径（可选）

### scripts/fetch_and_analyze.py

一站式获取并分析数据：

```bash
python scripts/fetch_and_analyze.py --fund-code 159730 --report-dir ./reports
```

## 使用示例

### 示例1：完整分析流程

```bash
# 1. 获取数据
python scripts/fetch_data.py --fund-code 159730 --output data_159730.json

# 2. 分析数据
python scripts/analyze_data.py --input data_159730.json --output analysis_159730.json --summary-text summary_159730.txt

# 3. 查看结果
cat summary_159730.txt
```

### 示例2：在Python代码中使用

```python
from scripts.analyzer import FundHeatmapAnalyzer

# 初始化分析器
analyzer = FundHeatmapAnalyzer()

# 分析数据
data = {...}  # API返回的JSON数据
report = analyzer.analyze(data)

# 获取结构化报告
json_report = report.to_json()

# 获取自然语言总结
text_summary = report.generate_summary()
```

## 内容生产工作流集成

本技能的输出可直接用于投资博客内容生产工作流：

1. **热力图截图引用**：使用分析结果中的关键信号选择截图引用点
2. **选题矩阵生成**：基于信号类型（分歧点、重仓看好等）生成选题
3. **深度调研指导**：为单股深度调研提供数据支持
4. **博客结构设计**：提供7段式博客结构的数据依据

## 参考文件

- [数据字段说明](references/data_fields.md)
- [分析算法详解](references/analysis_algorithms.md)
- [输出模板示例](references/output_templates.md)
- [内容生产指南](references/content_production.md)