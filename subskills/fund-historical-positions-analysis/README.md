# 基金历史持仓权重堆叠图分析技能

基于基金多季度持仓数据，分析历史持仓权重变化趋势，生成堆叠图数据和分析报告，支持投资博客内容生产工作流。

## 核心功能

1. **数据获取**：通过基金代码自动调用API获取多季度持仓明细数据
2. **时序数据分析**：解析多季度持仓数据，提取历史权重时序序列
3. **持仓稳定性分析**：分析各股票持仓权重的稳定性、变动趋势
4. **堆叠图数据生成**：生成用于历史持仓权重堆叠图的数据格式（quarter, ticker, portfolio_weight_pct）
5. **投资风格评估**：评估基金经理的投资风格（保守/激进）、持仓稳定性
6. **内容生产支持**：为投资博客内容生产提供关键信号和数据分析

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 快速分析示例

```bash
# 一站式获取、分析并生成完整报告
python scripts/quick_analysis.py --fund-code 159730 --output-dir ./reports
```

### 分步分析示例

```bash
# 1. 获取多季度持仓数据
python scripts/fetch_historical_data.py --fund-code 159730 --output historical_data.json --quarters 12

# 2. 分析历史持仓权重
python scripts/analyze_historical_weights.py --input historical_data.json --output stacked_data.csv --report analysis.json --summary summary.txt

# 3. 生成博客内容框架
python scripts/generate_blog_content.py --report analysis.json --output blog_framework.md --template 7segment
```

## 输出文件说明

| 文件类型 | 说明 | 用途 |
|----------|------|------|
| `stacked_data.csv` | 堆叠图数据 | 可视化历史持仓权重变化 |
| `analysis.json` | 结构化分析报告 | 程序化读取分析结果 |
| `summary.txt` | 自然语言总结 | 快速了解分析结论 |
| `blog_framework.md` | 博客内容框架 | 内容生产直接使用 |

## 数据格式

### 堆叠图数据格式（CSV）
```csv
quarter,ticker,portfolio_weight_pct
2025Q4,002050,14.78
2025Q4,000651,14.54
2025Q3,002050,15.31
```

### 分析报告格式（JSON）
包含以下关键部分：
- `metadata`: 分析元数据（基金代码、分析期间等）
- `stability_analysis`: 稳定性分析结果
- `trend_analysis`: 趋势分析结果
- `style_assessment`: 投资风格评估
- `key_signals`: 关键信号识别
- `recommendations`: 投资建议

## 内容生产工作流集成

本技能的输出可直接用于投资博客内容生产工作流：

1. **堆叠图数据引用**：使用生成的CSV数据创建历史持仓权重堆叠图
2. **选题矩阵生成**：基于分析结果生成稳定性、变动、风格等选题方向
3. **博客结构设计**：提供7段式博客结构（开篇、稳定性分析、变动趋势、风格评估、关键股票、风险评估、投资建议）
4. **双语输出支持**：分析结果支持中英文内容生产

## 脚本说明

### `scripts/fetch_historical_data.py`
获取基金多季度持仓数据
```bash
python scripts/fetch_historical_data.py --fund-code 159730 --output historical_data.json --quarters 8
```

### `scripts/analyze_historical_weights.py`
分析历史持仓权重数据
```bash
python scripts/analyze_historical_weights.py --input historical_data.json --output stacked_data.csv --report analysis.json --summary summary.txt
```

### `scripts/quick_analysis.py`
一站式获取、分析并生成完整报告
```bash
python scripts/quick_analysis.py --fund-code 159730 --output-dir ./reports --quarters 8
```

### `scripts/generate_blog_content.py`
基于分析结果生成博客内容框架
```bash
python scripts/generate_blog_content.py --report analysis.json --output blog_framework.md --template 7segment
```

## 参考文档

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

## 许可证

本项目采用MIT许可证。详见LICENSE文件（如有）。

## 免责声明

本工具提供的数据分析仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。