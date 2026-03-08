---
name: fund-dual-axis-analysis
description: "基金个股持仓双轴历史图分析技能，用于分析基金多季度持仓数据，生成个股持仓市值与股数双轴历史图数据和分析报告。当用户需要分析基金历史持仓数据、识别关键个股、生成双轴图CSV数据或分析大师收益表现时使用此技能。"
---

# 基金个股持仓双轴历史图分析技能

本技能用于分析基金多季度持仓数据，生成个股持仓市值与股数双轴历史图数据和分析报告，支持后续投资大师持仓分析内容生产工作流。

## 核心功能

1. **数据获取**：支持通过基金代码自动调用API获取多季度历史持仓数据
2. **个股精选**：基于权重、稳定性、收益表现等指标筛选关键个股
3. **双轴图数据生成**：生成个股持仓市值与股数双轴历史图CSV数据
4. **收益分析**：分析大师在个股上的收益表现，识别买入/卖出节点
5. **报告生成**：生成结构化JSON报告和自然语言分析总结
6. **工作流支持**：为投资博客内容生产提供数据支持

## 快速开始

### 方式一：通过基金代码分析（一站式）

```bash
# 使用脚本获取并分析数据，生成完整报告
python scripts/fetch_and_analyze.py --fund-code 159730 --report-dir ./reports --csv-dir ./csv_data
```

### 方式二：分步骤分析

```bash
# 1. 获取历史持仓数据
python scripts/fetch_historical_data.py --fund-code 159730 --quarters 12 --output historical_data.json

# 2. 分析数据并生成双轴图CSV
python scripts/analyze_dual_axis.py --input historical_data.json --output analysis.json --csv-dir ./csv_data --summary-text summary.txt
```

### 方式三：分析已有JSON数据

```bash
# 分析已获取的JSON数据
python scripts/analyze_dual_axis.py --input data.json --output analysis.json --csv-dir ./csv_data
```

## 数据字段说明

参见 [references/data_fields.md](references/data_fields.md) 了解完整的API返回字段说明。

## 分析逻辑

### 1. 个股精选逻辑

基于多季度持仓数据，筛选值得深入分析的关键个股：

| 筛选维度 | 指标 | 权重 | 解读 |
|---------|------|------|------|
| **持仓权重** | 平均权重 > 3% | 30% | 大师重仓股，代表核心持仓 |
| **持仓稳定性** | 持仓季度数 / 总季度数 > 0.7 | 25% | 长期稳定持有，代表深度研究 |
| **权重变化趋势** | 权重变化斜率 > 0 | 20% | 持续加仓，代表看好程度提升 |
| **收益表现** | 市值斜率 > 股数斜率 | 15% | 正收益表现，代表成功投资 |
| **行业代表性** | 行业龙头或代表 | 10% | 行业代表性，便于行业分析 |

### 2. 双轴图数据分析

基于CSV格式数据生成双轴图：

```csv
quarter,ticker,market_value_100m,shares_million
2022Q4,002050,5.19,93.8
2023Q1,002050,5.54,114.3
2023Q2,002050,5.19,93.8
```

**图表内容**：
- **左轴（柱状）**：该股持仓市值变化（100M为单位）
- **右轴（折线）**：该股持仓股数变化（百万股为单位）
- **两条曲线的相对斜率**：判断大师收益的直观方式

### 3. 收益分析逻辑

**核心判断原则**：市值曲线的斜率 > 股数曲线的斜率 → 大师在该股上存在正收益

**四种斜率组合分析**：

| 市值斜率 | 股数斜率 | 收益判断 | 解读 |
|---------|---------|---------|------|
| ↗ 上升 | ↗ 上升 | 正收益 | 价格上涨 + 加仓 = 强烈看好 |
| ↗ 上升 | → 持平 | 正收益 | 价格上涨 + 持仓不变 = 被动收益 |
| ↗ 上升 | ↘ 下降 | 正收益 | 价格上涨 > 减仓 = 获利了结 |
| → 持平 | ↗ 上升 | 负收益 | 价格不变 + 加仓 = 成本增加 |
| ↘ 下降 | ↗ 上升 | 负收益 | 价格下跌 + 加仓 = 越跌越买 |
| ↘ 下降 | ↘ 下降 | 负收益 | 价格下跌 + 减仓 = 止损离场 |

### 4. 关键节点识别

识别大师操作的关键时间节点：

1. **大幅加仓节点**：股数环比增长 > 20%
2. **大幅减仓节点**：股数环比下降 > 20%
3. **收益拐点**：市值斜率与股数斜率关系变化
4. **持仓峰值**：持仓市值最高点
5. **持仓谷值**：持仓市值最低点

## 输出结构

### 结构化JSON报告

报告包含以下部分：

```json
{
  "metadata": {
    "fund_code": "159730",
    "fund_name": "博时国证龙头家电ETF",
    "analysis_date": "2026-03-07",
    "total_quarters": 12,
    "total_stocks": 10,
    "analysis_version": "1.0.0"
  },
  "key_stocks_selection": {
    "selection_criteria": {...},
    "selected_stocks": [...],
    "selection_scores": {...}
  },
  "dual_axis_analysis": {
    "csv_data_samples": {...},
    "slope_analysis": {...},
    "profit_analysis": {...}
  },
  "operation_nodes": {
    "significant_increases": [...],
    "significant_decreases": [...],
    "profit_turning_points": [...]
  },
  "blog_content_support": {
    "visualization_suggestions": [...],
    "key_insights": [...],
    "content_outline": {...}
  },
  "recommendations": {
    "focus_stocks": [...],
    "analysis_priorities": [...],
    "risk_considerations": [...]
  }
}
```

### 双轴图CSV数据

为每个关键个股生成CSV文件：

```csv
quarter,ticker,market_value_100m,shares_million
2022Q4,002050,5.19,93.8
2023Q1,002050,5.54,114.3
2023Q2,002050,5.19,93.8
2023Q3,002050,5.19,93.8
2023Q4,002050,5.19,93.8
2024Q1,002050,5.54,114.3
2024Q2,002050,5.19,93.8
2024Q3,002050,5.19,93.8
2024Q4,002050,5.19,93.8
2025Q1,002050,5.54,114.3
2025Q2,002050,5.19,93.8
2025Q3,002050,5.19,93.8
```

### 自然语言分析总结

生成中文分析文本，包含：
- 关键个股精选结果
- 双轴图数据分析发现
- 大师收益表现评估
- 操作节点识别
- 博客内容生产建议

## 脚本说明

### scripts/fetch_historical_data.py

获取基金多季度历史持仓数据：

```bash
python scripts/fetch_historical_data.py --fund-code 159730 --quarters 12 --output historical_data.json
```

参数：
- `--fund-code`: 基金代码（必需）
- `--quarters`: 分析季度数（可选，默认：12）
- `--output`: 输出文件路径（可选，默认：historical_fund_data.json）

### scripts/analyze_dual_axis.py

分析历史持仓数据，生成双轴图分析：

```bash
python scripts/analyze_dual_axis.py --input historical_data.json --output analysis.json --csv-dir ./csv_data
```

参数：
- `--input`: 输入JSON文件路径（必需）
- `--output`: 结构化分析报告输出路径（可选）
- `--csv-dir`: CSV数据输出目录（可选）
- `--summary-text`: 自然语言总结输出路径（可选）
- `--top-n`: 分析前N个关键个股（可选，默认：5）

### scripts/fetch_and_analyze.py

一站式获取并分析数据：

```bash
python scripts/fetch_and_analyze.py --fund-code 159730 --report-dir ./reports --csv-dir ./csv_data
```

## 使用示例

### 示例1：完整分析流程

```bash
# 1. 获取历史数据
python scripts/fetch_historical_data.py --fund-code 159730 --quarters 12 --output data_159730.json

# 2. 分析数据并生成CSV
python scripts/analyze_dual_axis.py --input data_159730.json --output analysis_159730.json --csv-dir ./csv_159730 --summary-text summary_159730.txt

# 3. 查看结果
cat summary_159730.txt
ls ./csv_159730/*.csv
```

### 示例2：在Python代码中使用

```python
from scripts.analyzer import FundDualAxisAnalyzer

# 初始化分析器
analyzer = FundDualAxisAnalyzer()

# 分析数据
data = {...}  # API返回的JSON数据
report = analyzer.analyze(data)

# 获取结构化报告
json_report = report.to_json()

# 获取CSV数据
csv_data = report.generate_csv_data()

# 获取自然语言总结
text_summary = report.generate_summary()
```

## 内容生产工作流集成

本技能的输出可直接用于投资博客内容生产工作流：

### 1. 双轴图截图引用
- 使用分析结果中的关键个股选择截图引用点
- 基于斜率分析确定最有故事性的图表
- 生成图表说明文字模板

### 2. 选题矩阵生成
- 基于收益分析结果（正收益/负收益）生成选题
- 基于操作节点（加仓/减仓）生成时间线故事
- 基于行业分布生成行业分析选题

### 3. 深度调研指导
- 为单股深度调研提供历史数据支持
- 识别需要重点分析的时间段
- 提供对比分析框架（同行业对比、不同大师对比）

### 4. 博客结构设计
- 提供7段式博客结构的数据依据：
  1. 引言：大师概况 + 关键发现
  2. 数据概览：基金基本信息 + 分析范围
  3. 关键个股精选：筛选逻辑 + 结果展示
  4. 双轴图深度分析：图表解读 + 收益分析
  5. 操作节点分析：加仓/减仓时机 + 收益拐点
  6. 行业洞察：行业分布 + 代表性分析
  7. 投资启示：经验总结 + 风险提示

### 5. 可视化建议
- 图表类型建议：双轴图、趋势线、散点图
- 颜色方案建议：收益正负用红绿色系
- 标注建议：关键节点标注、趋势线标注

## 参考文件

- [数据字段说明](references/data_fields.md)
- [分析算法详解](references/analysis_algorithms.md)
- [输出模板示例](references/output_templates.md)
- [内容生产指南](references/content_production.md)