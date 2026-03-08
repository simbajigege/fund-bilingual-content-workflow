---
name: fund-historical-positions-analysis
description: "基金历史持仓权重堆叠图分析技能，用于解析基金多季度持仓数据，分析持仓稳定性、变动趋势，生成堆叠图数据格式。当用户需要分析基金历史持仓权重、生成堆叠图数据、分析持仓稳定性与变动趋势、评估投资大师风格时使用此技能。支持通过基金代码获取多季度持仓数据，提取quarter、ticker、portfolio_weight_pct关键字段，为投资博客内容生产提供数据支持。"
---

# 基金历史持仓权重堆叠图分析技能

本技能用于分析基金多季度持仓数据，提取历史持仓权重时序数据，生成堆叠图数据格式，分析持仓稳定性和变动趋势，支持投资大师持仓分析内容生产工作流。

## 核心功能

1. **数据获取**：支持通过基金代码自动调用API获取多季度持仓明细数据
2. **时序数据分析**：解析多季度持仓数据，提取历史权重时序序列
3. **持仓稳定性分析**：分析各股票持仓权重的稳定性、变动趋势
4. **堆叠图数据生成**：生成用于历史持仓权重堆叠图的数据格式（quarter, ticker, portfolio_weight_pct）
5. **投资风格评估**：评估基金经理的投资风格（保守/激进）、持仓稳定性
6. **内容生产支持**：为投资博客内容生产提供关键信号和数据分析

## 快速开始

### 方式一：通过基金代码分析

```bash
# 获取并分析基金多季度持仓数据
python scripts/fetch_historical_data.py --fund-code 159730 --output historical_data.json

# 分析历史持仓权重
python scripts/analyze_historical_weights.py --input historical_data.json --output stacked_chart_data.csv
```

### 方式二：分析已有JSON数据

```bash
# 分析已获取的多季度持仓数据
python scripts/analyze_historical_weights.py --input historical_data.json --output stacked_chart_data.csv --report analysis_report.json
```

## 数据格式说明

### 输入数据格式

API返回的多季度持仓数据格式：
```json
{
  "master_code": "159730",
  "items": [
    {
      "id": 860,
      "master_code": "159730",
      "master_name": "博时国证龙头家电ETF",
      "master_description": "基金 159730(博时国证龙头家电ETF) 2025年4季度股票投资明细 的持仓数据",
      "a_positions": [
        {
          "shares": 93800.00000000001,
          "weight": 14.78,
          "stock_code": "002050",
          "stock_name": "三花智控",
          "market_value": 5188099.999999999
        }
      ],
      "hk_positions": [],
      "us_positions": [],
      "as_of_date": "2025-12-01",
      "created_at": "2026-03-02T18:58:17.290150",
      "updated_at": "2026-03-02T18:58:17.290150"
    }
  ],
  "total": 12
}
```

### 输出数据格式

堆叠图数据格式（CSV）：
```csv
quarter,ticker,portfolio_weight_pct
2025Q4,002050,14.78
2025Q4,000651,14.54
2025Q3,002050,15.31
2025Q3,600690,13.37
```

分析报告格式（JSON）：
```json
{
  "metadata": {
    "fund_code": "159730",
    "analysis_date": "2026-03-07",
    "quarters_analyzed": 4,
    "unique_stocks": 10,
    "total_positions": 40
  },
  "stability_analysis": {
    "stability_score": 85.2,
    "high_stability_stocks": [...],
    "high_volatility_stocks": [...],
    "quarterly_turnover_rate": 12.5
  },
  "trend_analysis": {
    "increasing_trend_stocks": [...],
    "decreasing_trend_stocks": [...],
    "new_entrants": [...],
    "exited_stocks": [...]
  },
  "stacked_chart_data": [...],
  "key_signals": [...],
  "recommendations": {...}
}
```

## 分析逻辑

### 1. 持仓稳定性分析

基于各股票历史权重序列计算稳定性指标：

| 指标 | 计算方法 | 解读 |
|------|----------|------|
| 权重标准差 | 计算各股票权重的时间序列标准差 | 标准差越小，持仓越稳定 |
| 权重变动率 | (max_weight - min_weight) / avg_weight | 变动率越小，持仓越稳定 |
| 持仓连续性 | 连续出现在持仓中的季度数 / 总季度数 | 连续性越高，核心持仓越明确 |
| 排名稳定性 | 各季度持仓排名变动程度 | 排名稳定，投资逻辑一致 |

### 2. 变动趋势分析

识别持仓权重变动模式：

| 趋势类型 | 识别条件 | 解读 |
|----------|----------|------|
| 持续加仓 | 连续3个季度权重递增 | 基金经理持续看好，主动加仓 |
| 持续减仓 | 连续3个季度权重递减 | 基金经理逐步退出，注意风险 |
| 新进持仓 | 最近季度新出现的股票 | 基金经理新建仓位，关注逻辑 |
| 退出持仓 | 最近季度消失的股票 | 基金经理清仓退出，分析原因 |
| 权重波动 | 权重上下震荡无明确趋势 | 波段操作或调仓频繁 |

### 3. 投资风格评估

基于整体持仓变动情况评估投资风格：

| 风格类型 | 特征 | 适合跟踪程度 |
|----------|------|--------------|
| 保守稳定型 | 持仓结构长期稳定，季度变动率<10% | 高 - 适合普通投资者跟踪 |
| 适度调整型 | 适度调整持仓，季度变动率10-30% | 中 - 需要一定分析能力 |
| 积极调整型 | 频繁调整持仓，季度变动率>30% | 低 - 普通投资者跟踪困难 |

### 4. 堆叠图读图方法

基于生成的堆叠图数据，提供专业读图指导：

| 观察点 | 解读方向 | 内容生产价值 |
|--------|----------|--------------|
| 某色块长期占比稳定 | 大师核心持仓，高确定性 | 适合普通人"抄作业" |
| 某色块快速扩大 | 大师正在主动加仓 | 需关注其投资逻辑 |
| 某色块快速缩小 | 大师在减仓 | 注意风险信号 |
| 整体结构长期稳定 | 风格保守，持仓稳定性高 | 跟踪难度低 |
| 整体结构频繁变动 | 风格激进，调仓频繁 | 跟踪风险高 |

## 13F数据滞后说明

**重要提醒**：基金持仓数据存在披露延迟（通常45天）。这意味着：

- **对于持仓稳定的大师**：滞后影响极小，适合跟踪
- **对于持仓频繁变动的大师**：45天延迟可能导致信号失效

在内容生产中需明确说明这一限制，并将"持仓稳定性"作为选题判断依据。

## 脚本说明

### scripts/fetch_historical_data.py

获取基金多季度持仓数据：

```bash
python scripts/fetch_historical_data.py --fund-code 159730 --output historical_data.json --quarters 8
```

参数：
- `--fund-code`: 基金代码（必需）
- `--output`: 输出文件路径（可选，默认：historical_data.json）
- `--quarters`: 分析季度数（可选，默认：8，即最近8个季度）
- `--include-all`: 包含所有历史数据（可选，可能数据量较大）

### scripts/analyze_historical_weights.py

分析历史持仓权重数据：

```bash
python scripts/analyze_historical_weights.py --input historical_data.json --output stacked_data.csv --report analysis.json --summary summary.txt
```

参数：
- `--input`: 输入JSON文件路径（必需）
- `--output`: 堆叠图数据输出路径（可选，CSV格式）
- `--report`: 结构化分析报告输出路径（可选，JSON格式）
- `--summary`: 自然语言总结输出路径（可选）
- `--min-weight`: 最小权重阈值（可选，默认：0.5%，低于此值忽略）
- `--stability-threshold`: 稳定性阈值（可选，默认：70分）

### scripts/generate_blog_content.py

基于分析结果生成博客内容框架：

```bash
python scripts/generate_blog_content.py --report analysis.json --output blog_framework.md
```

参数：
- `--report`: 分析报告文件路径（必需）
- `--output`: 博客内容框架输出路径（可选）
- `--template`: 模板类型（可选：simple/detailed/7segment，默认：7segment）

## 使用示例

### 示例1：完整分析流程

```bash
# 1. 获取多季度持仓数据
python scripts/fetch_historical_data.py --fund-code 159730 --output data_159730.json --quarters 12

# 2. 分析历史持仓权重
python scripts/analyze_historical_weights.py --input data_159730.json --output stacked_159730.csv --report analysis_159730.json --summary summary_159730.txt

# 3. 生成博客内容框架
python scripts/generate_blog_content.py --report analysis_159730.json --output blog_159730.md

# 4. 查看关键结果
cat summary_159730.txt
```

### 示例2：快速分析并生成堆叠图数据

```bash
# 一站式获取、分析并输出堆叠图数据
python scripts/quick_analysis.py --fund-code 159730 --output-dir ./reports
```

## 内容生产工作流集成

本技能的输出可直接用于投资博客内容生产工作流：

### 1. 堆叠图数据引用
- 使用生成的CSV数据创建历史持仓权重堆叠图
- 在博客中引用图表，说明各色块含义

### 2. 选题矩阵生成
基于分析结果生成选题方向：
- **稳定性选题**：分析持仓稳定的核心股票
- **变动选题**：分析加仓/减仓的股票逻辑
- **风格选题**：评估基金经理的投资风格
- **风险选题**：提示持仓频繁变动的风险

### 3. 博客结构设计
提供7段式博客结构：
1. 开篇：堆叠图全景展示
2. 稳定性分析：哪些是核心持仓
3. 变动趋势：加仓/减仓信号解读
4. 风格评估：基金经理风格分析
5. 关键股票：重点股票深度分析
6. 风险评估：13F数据滞后影响
7. 投资建议：适合的投资者类型

### 4. 双语输出支持
分析结果支持中英文内容生产：
- 中文版：包含A股市场类比
- 英文版：不含中国市场类比

## 参考文件

- [数据字段说明](references/data_fields.md) - 详细的API返回字段说明
- [分析算法详解](references/analysis_algorithms.md) - 稳定性、趋势分析算法
- [输出模板示例](references/output_templates.md) - 各种输出格式示例
- [内容生产指南](references/content_production.md) - 博客内容生产工作流

## 常见问题

### Q1: 数据更新频率如何？
A: 基金季度持仓数据通常在季度结束后45天内披露，API会及时更新最新数据。

### Q2: 如何处理缺失的季度数据？
A: 分析脚本会自动处理缺失数据，使用线性插值或标记为缺失，确保时间序列连续性。

### Q3: 权重百分比之和不等于100%？
A: 由于四舍五入和最小权重过滤，总和可能略偏离100%，通常误差在±1%范围内可接受。

### Q4: 如何选择分析的季度数？
A: 建议分析最近8-12个季度（2-3年），既能观察趋势又不会数据过于陈旧。

### Q5: 稳定性评分如何解读？
A: 0-100分，>80分表示高度稳定，60-80分表示适度稳定，<60分表示频繁变动。