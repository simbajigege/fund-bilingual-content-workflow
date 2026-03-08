# 输出模板示例

本文档提供基金个股持仓双轴历史图分析的各种输出模板示例。

## 目录

1. [结构化JSON报告模板](#结构化json报告模板)
2. [双轴图CSV数据模板](#双轴图csv数据模板)
3. [自然语言分析总结模板](#自然语言分析总结模板)
4. [博客内容建议模板](#博客内容建议模板)
5. [可视化建议模板](#可视化建议模板)
6. [SEO元数据模板](#seo元数据模板)

## 结构化JSON报告模板

### 完整报告结构

```json
{
  "metadata": {
    "fund_code": "159730",
    "fund_name": "博时国证龙头家电ETF",
    "analysis_date": "2026-03-07",
    "total_quarters": 12,
    "quarters_analyzed": 8,
    "total_stocks": 10,
    "analysis_version": "1.0.0",
    "analysis_timestamp": "2026-03-07T14:30:00Z",
    "config_used": "default"
  },
  "data_summary": {
    "time_range": {
      "start_date": "2023-12-01",
      "end_date": "2025-12-01",
      "quarters": ["2023Q4", "2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4"]
    },
    "market_coverage": {
      "a_positions_count": 10,
      "hk_positions_count": 0,
      "us_positions_count": 0
    },
    "data_quality": {
      "completeness_score": 95.0,
      "consistency_score": 92.5,
      "validation_passed": true,
      "issues_found": []
    }
  },
  "key_stocks_selection": {
    "selection_criteria": {
      "min_avg_weight": 3.0,
      "min_quarters_held_ratio": 0.7,
      "max_stocks_to_select": 5,
      "weights": {
        "avg_weight": 0.3,
        "holding_stability": 0.25,
        "weight_trend": 0.2,
        "profit_performance": 0.15,
        "industry_representation": 0.1
      }
    },
    "candidate_stocks": [
      {
        "stock_code": "002050",
        "stock_name": "三花智控",
        "avg_weight": 14.85,
        "quarters_held": 8,
        "quarters_held_ratio": 1.0,
        "weight_slope": 0.15,
        "market_value_slope": 0.12,
        "shares_slope": 0.08,
        "industry_rank": 1,
        "scores": {
          "avg_weight_score": 95.0,
          "holding_stability_score": 100.0,
          "weight_trend_score": 75.0,
          "profit_performance_score": 80.0,
          "industry_representation_score": 100.0
        },
        "comprehensive_score": 89.5,
        "selection_reason": "行业龙头，持仓稳定，收益表现良好"
      }
    ],
    "selected_stocks": [
      {
        "rank": 1,
        "stock_code": "002050",
        "stock_name": "三花智控",
        "final_score": 89.5,
        "selection_priority": "high",
        "analysis_recommendation": "建议重点分析，收益表现优秀"
      },
      {
        "rank": 2,
        "stock_code": "000651",
        "stock_name": "格力电器",
        "final_score": 82.3,
        "selection_priority": "medium",
        "analysis_recommendation": "建议分析，持仓权重较高"
      }
    ],
    "selection_scores": {
      "score_distribution": {
        "90-100": 1,
        "80-89": 2,
        "70-79": 3,
        "60-69": 2,
        "below_60": 2
      },
      "average_score": 75.8,
      "median_score": 78.2,
      "selection_threshold": 70.0
    }
  },
  "dual_axis_analysis": {
    "csv_data_samples": {
      "002050": {
        "header": ["quarter", "ticker", "market_value_100m", "shares_million"],
        "sample_rows": [
          ["2024Q1", "002050", 5.54, 114.3],
          ["2024Q2", "002050", 5.19, 93.8],
          ["2024Q3", "002050", 5.19, 93.8]
        ],
        "file_path": "./csv_data/002050_dual_axis.csv"
      }
    },
    "slope_analysis": {
      "002050": {
        "market_value_slope": 0.12,
        "shares_slope": 0.08,
        "profit_differential": 0.04,
        "slope_calculation_method": "linear_regression",
        "slope_confidence": 0.92,
        "r_squared": 0.85
      }
    },
    "profit_analysis": {
      "002050": {
        "profit_type": "positive_profit",
        "profit_strength": "moderate_positive",
        "profit_differential_percentage": 4.2,
        "profit_contribution_breakdown": {
          "price_contribution": 65.0,
          "shares_contribution": 35.0
        },
        "estimated_annual_return": 15.8,
        "risk_adjusted_return": 1.25
      }
    },
    "trend_analysis": {
      "002050": {
        "market_value_trend": "uptrend",
        "shares_trend": "slight_uptrend",
        "combined_trend": "positive_profit_trend",
        "trend_strength": "moderate",
        "trend_consistency": "consistent"
      }
    }
  },
  "operation_nodes": {
    "significant_increases": [
      {
        "stock_code": "002050",
        "stock_name": "三花智控",
        "quarter": "2024Q1",
        "previous_shares": 93.8,
        "current_shares": 114.3,
        "change_pct": 21.9,
        "market_value_before": 5.19,
        "market_value_after": 5.54,
        "context": "大幅加仓，可能是看好后市表现",
        "significance_level": "high"
      }
    ],
    "significant_decreases": [
      {
        "stock_code": "002050",
        "stock_name": "三花智控",
        "quarter": "2024Q2",
        "previous_shares": 114.3,
        "current_shares": 93.8,
        "change_pct": -17.9,
        "market_value_before": 5.54,
        "market_value_after": 5.19,
        "context": "部分获利了结，但仍保持较高仓位",
        "significance_level": "medium"
      }
    ],
    "profit_turning_points": [
      {
        "stock_code": "002050",
        "stock_name": "三花智控",
        "quarter": "2024Q3",
        "previous_profit_type": "neutral",
        "current_profit_type": "positive_profit",
        "profit_differential_change": 0.05,
        "context": "收益拐点，开始实现正收益",
        "significance_level": "high"
      }
    ],
    "peaks_and_valleys": {
      "market_value_peaks": [
        {
          "stock_code": "002050",
          "stock_name": "三花智控",
          "quarter": "2024Q1",
          "market_value": 5.54,
          "type": "peak",
          "peak_strength": "strong"
        }
      ],
      "market_value_valleys": [
        {
          "stock_code": "002050",
          "stock_name": "三花智控",
          "quarter": "2024Q2",
          "market_value": 5.19,
          "type": "valley",
          "valley_depth": "shallow"
        }
      ]
    }
  },
  "industry_analysis": {
    "industry_distribution": [
      {
        "industry_name": "家用电器",
        "total_weight": 68.5,
        "stock_count": 6,
        "average_weight": 11.4,
        "key_stocks": ["002050", "000651", "000333"],
        "industry_trend": "stable"
      },
      {
        "industry_name": "机械设备",
        "total_weight": 12.3,
        "stock_count": 2,
        "average_weight": 6.15,
        "key_stocks": ["603486", "688169"],
        "industry_trend": "growing"
      }
    ],
    "concentration_analysis": {
      "top_3_industries_weight": 80.8,
      "herfindahl_index": 0.25,
      "concentration_level": "moderate",
      "risk_assessment": "low"
    }
  },
  "blog_content_support": {
    "visualization_suggestions": [
      {
        "chart_type": "dual_axis",
        "recommended_stocks": ["002050", "000651"],
        "chart_title": "三花智控持仓市值与股数双轴历史图",
        "chart_subtitle": "市值斜率 > 股数斜率，显示正收益表现",
        "color_scheme": "profit_positive",
        "annotations": [
          {
            "quarter": "2024Q1",
            "text": "大幅加仓节点",
            "type": "increase"
          },
          {
            "quarter": "2024Q3",
            "text": "收益拐点",
            "type": "turning_point"
          }
        ]
      }
    ],
    "key_insights": [
      {
        "insight_type": "profit_analysis",
        "title": "三花智控：收益表现优秀",
        "content": "大师在三花智控上实现了显著正收益，市值增长率超过股数增长率，表明股价上涨贡献主要收益。",
        "data_support": "市值斜率0.12 > 股数斜率0.08，收益差4.2%",
        "priority": "high"
      },
      {
        "insight_type": "operation_timing",
        "title": "精准的加仓时机",
        "content": "在2024Q1大幅加仓21.9%，随后股价上涨，显示良好的择时能力。",
        "data_support": "加仓后市值增长6.7%",
        "priority": "medium"
      }
    ],
    "content_outline": {
      "template_name": "7_segment_blog",
      "segments": [
        {
          "segment_number": 1,
          "title": "引言：博时国证龙头家电ETF持仓分析",
          "key_points": [
            "基金概况和投资策略",
            "分析时间范围和数据来源",
            "核心发现预览"
          ],
          "suggested_length": "200-300字"
        },
        {
          "segment_number": 2,
          "title": "数据概览：持仓结构与时间范围",
          "key_points": [
            "基金基本信息和规模",
            "分析的时间跨度和季度数",
            "持仓股票数量和市场分布"
          ],
          "suggested_length": "150-250字"
        },
        {
          "segment_number": 3,
          "title": "关键个股精选：谁值得重点关注？",
          "key_points": [
            "精选逻辑和评分体系",
            "前5大关键个股介绍",
            "各维度得分分析"
          ],
          "suggested_length": "300-400字"
        },
        {
          "segment_number": 4,
          "title": "双轴图深度分析：大师的收益密码",
          "key_points": [
            "双轴图解读方法",
            "关键个股收益分析",
            "斜率组合和收益类型"
          ],
          "suggested_length": "400-500字",
          "chart_references": ["002050_dual_axis_chart"]
        },
        {
          "segment_number": 5,
          "title": "操作节点分析：加减仓的艺术",
          "key_points": [
            "大幅加仓/减仓节点",
            "收益拐点识别",
            "操作时机评估"
          ],
          "suggested_length": "300-400字"
        },
        {
          "segment_number": 6,
          "title": "行业洞察：家电行业的持仓逻辑",
          "key_points": [
            "行业分布分析",
            "龙头股选择逻辑",
            "行业趋势判断"
          ],
          "suggested_length": "250-350字"
        },
        {
          "segment_number": 7,
          "title": "投资启示：我们能学到什么？",
          "key_points": [
            "大师投资风格总结",
            "可复制的投资策略",
            "风险提示和注意事项"
          ],
          "suggested_length": "200-300字"
        }
      ],
      "total_estimated_length": "1800-2500字"
    }
  },
  "recommendations": {
    "focus_stocks": [
      {
        "stock_code": "002050",
        "stock_name": "三花智控",
        "recommendation_reason": "收益表现最佳，持仓稳定，行业龙头",
        "analysis_priority": "highest",
        "suggested_analysis_depth": "deep"
      },
      {
        "stock_code": "000651",
        "stock_name": "格力电器",
        "recommendation_reason": "权重高，操作节点明显，有故事性",
        "analysis_priority": "high",
        "suggested_analysis_depth": "medium"
      }
    ],
    "analysis_priorities": [
      {
        "priority": 1,
        "task": "深度分析三花智控的收益来源",
        "reason": "收益表现最突出，可作为核心案例"
      },
      {
        "priority": 2,
        "task": "对比分析不同家电股的表现差异",
        "reason": "了解大师在家电行业内的选股偏好"
      },
      {
        "priority": 3,
        "task": "分析操作节点的市场背景",
        "reason": "理解加减仓时的市场环境和时机选择"
      }
    ],
    "risk_considerations": [
      {
        "risk_type": "concentration_risk",
        "description": "基金在家电行业集中度较高",
        "severity": "medium",
        "mitigation": "建议分析时说明行业集中度的利弊"
      },
      {
        "risk_type": "data_limitation",
        "description": "数据时间跨度有限（2年）",
        "severity": "low",
        "mitigation": "在分析中注明时间范围限制"
      }
    ]
  },
  "performance_metrics": {
    "analysis_duration_ms": 2450,
    "memory_usage_mb": 85.3,
    "stocks_processed": 10,
    "quarters_processed": 8,
    "algorithms_used": ["linear_regression", "peak_detection", "trend_analysis"]
  }
}
```

### 简化报告模板

```json
{
  "fund_code": "159730",
  "fund_name": "博时国证龙头家电ETF",
  "analysis_date": "2026-03-07",
  "key_findings": {
    "top_stocks": [
      {"stock_code": "002050", "stock_name": "三花智控", "score": 89.5},
      {"stock_code": "000651", "stock_name": "格力电器", "score": 82.3}
    ],
    "best_performing": {
      "stock_code": "002050",
      "stock_name": "三花智控",
      "profit_differential": 0.04
    },
    "significant_operations": [
      {"quarter": "2024Q1", "stock": "002050", "type": "increase", "change_pct": 21.9}
    ]
  },
  "recommendations": {
    "focus_analysis": ["002050"],
    "generate_csv": true,
    "blog_topics": ["三花智控的收益分析", "家电ETF的持仓逻辑"]
  }
}
```

## 双轴图CSV数据模板

### 单个股票CSV模板

```csv
quarter,ticker,market_value_100m,shares_million
2023Q4,002050,4.88,89.2
2024Q1,002050,5.54,114.3
2024Q2,002050,5.19,93.8
2024Q3,002050,5.19,93.8
2024Q4,002050,5.32,97.5
2025Q1,002050,5.76,118.6
2025Q2,002050,5.41,99.3
2025Q3,002050,5.41,99.3
2025Q4,002050,5.19,93.8
```

### 合并所有股票CSV模板

```csv
quarter,ticker,market_value_100m,shares_million,stock_name,weight
2023Q4,002050,4.88,89.2,三花智控,14.2
2024Q1,002050,5.54,114.3,三花智控,15.3
2023Q4,000651,4.22,106.4,格力电器,11.7
2024Q1,000651,4.22,106.4,格力电器,11.7
2023Q4,000333,4.58,63.1,美的集团,12.7
2024Q1,000333,4.58,63.1,美的集团,12.7
```

### CSV文件命名规范

```
{stock_code}_{fund_code}_dual_axis.csv
```

示例：
- `002050_159730_dual_axis.csv`
- `all_stocks_159730_dual_axis.csv` (合并文件)

## 自然语言分析总结模板

### 完整总结模板

```
# 基金个股持仓双轴历史图分析报告

## 基本信息
- **基金代码**: 159730
- **基金名称**: 博时国证龙头家电ETF
- **分析日期**: 2026年3月7日
- **数据范围**: 2023年Q4 - 2025年Q4（共8个季度）
- **分析版本**: 1.0.0

## 关键发现摘要

### 1. 精选个股表现
通过对10只持仓股票的综合评分，筛选出5只关键个股：

1. **三花智控 (002050)** - 综合评分89.5分
   - 平均权重：14.85%，行业龙头
   - 持仓稳定性：100%（8个季度连续持有）
   - 收益表现：市值斜率(0.12) > 股数斜率(0.08)，正收益4.2%

2. **格力电器 (000651)** - 综合评分82.3分
   - 平均权重：12.5%，权重稳定
   - 操作节点：2024Q1小幅加仓5.3%

### 2. 收益分析核心结论
- **最佳收益表现**：三花智控，收益差4.2%，主要来自股价上涨
- **正收益股票**：3只（占总持仓权重45%）
- **负收益股票**：1只（占总持仓权重8%）
- **中性收益**：6只（占总持仓权重47%）

### 3. 重要操作节点
1. **大幅加仓**：2024Q1，三花智控加仓21.9%
2. **收益拐点**：2024Q3，三花智控从中性收益转为正收益
3. **持仓峰值**：2024Q1，总持仓市值达到峰值

### 4. 行业分布特征
- **主要行业**：家用电器（68.5%）、机械设备（12.3%）
- **集中度**：前3大行业占比80.8%，集中度中等
- **龙头偏好**：明显偏好行业龙头股

## 详细分析

### 双轴图分析亮点
1. **三花智控双轴图显示**：
   - 市值曲线整体上升趋势明显
   - 股数曲线波动较大，显示主动管理
   - 2024Q1大幅加仓后，市值持续增长

2. **收益类型分布**：
   - 正收益型：3只（主要来自股价上涨）
   - 负收益型：1只（股数增加但市值下降）
   - 中性型：6只（市值与股数同步变化）

### 大师操作风格分析
1. **择时能力**：在关键节点有明确操作（如2024Q1加仓）
2. **行业专注**：集中投资熟悉的家电行业
3. **龙头偏好**：优先选择行业龙头公司
4. **收益导向**：注重市值增长，适时获利了结

## 博客内容生产建议

### 推荐选题
1. **核心选题**：《三花智控：大师如何在家电龙头股上赚取15.8%年化收益？》
2. **操作分析**：《从加减仓节点看大师的择时艺术》
3. **行业洞察**：《家电ETF的持仓逻辑：为什么只买龙头？》

### 可视化建议
1. **必选图表**：三花智控双轴历史图（标注加仓节点和收益拐点）
2. **辅助图表**：关键个股收益对比图、行业分布饼图
3. **颜色方案**：正收益用绿色系，负收益用红色系

### 内容结构建议
采用7段式结构：
1. 引言：基金概况 + 核心发现
2. 数据概览：分析范围和方法
3. 关键个股：精选逻辑和结果
4. 双轴图分析：图表解读和收益分析
5. 操作节点：加减仓时机分析
6. 行业洞察：持仓逻辑和行业分布
7. 投资启示：经验总结和风险提示

## 风险提示
1. **数据局限性**：分析基于过去2年数据，长期趋势需谨慎判断
2. **行业集中风险**：基金高度集中在家电行业，受行业周期影响较大
3. **市场风险**：历史表现不代表未来，投资需谨慎

---

*报告生成时间：2026-03-07T14:30:00Z*
*分析工具：基金个股持仓双轴历史图分析技能 v1.0.0*
```

### 简短总结模板

```
基金159730（博时国证龙头家电ETF）持仓分析完成。

**关键发现**：
1. 精选5只关键个股，三花智控(002050)评分最高（89.5分）
2. 三花智控实现正收益4.2%，主要来自股价上涨
3. 2024Q1大幅加仓21.9%，显示看好后市

**推荐行动**：
1. 重点分析三花智控的收益来源
2. 生成双轴图CSV数据用于可视化
3. 基于操作节点构建投资故事

详细报告已保存至：analysis_159730.json
```

## 博客内容建议模板

### 7段式博客大纲模板

```markdown
# [博客标题]：基于[基金名称]持仓数据的深度分析

## 1. 引言：为什么关注这只基金？
- 基金基本信息：代码、名称、管理规模
- 投资策略和风格概述
- 本次分析的核心价值和目标

## 2. 数据概览：我们分析了什么？
- 数据来源和时间范围
- 分析方法论简介
- 关键指标预览

## 3. 关键个股精选：谁值得重点关注？
- 精选逻辑和评分体系
- 前3-5名关键个股介绍
- 各维度得分分析

## 4. 双轴图深度分析：大师的收益密码
- 双轴图解读方法教学
- 关键个股的收益表现
- 斜率组合分析（四种类型）

## 5. 操作节点分析：加减仓的艺术
- 重大加仓/减仓节点
- 收益拐点识别
- 操作时机评估

## 6. 行业洞察：[行业名]的持仓逻辑
- 行业分布分析
- 龙头股选择逻辑
- 行业趋势判断

## 7. 投资启示：我们能学到什么？
- 大师投资风格总结
- 可复制的投资策略
- 风险提示和注意事项

---

**可视化图表引用**：
- [图1] 三花智控持仓市值与股数双轴历史图
- [图2] 关键个股收益对比图
- [图3] 行业分布饼图

**数据来源**：基金季度持仓报告，分析时间[日期]
```

### 图表说明文字模板

```markdown
**[图1] 三花智控持仓市值与股数双轴历史图**
- 柱状图：持仓市值变化（单位：亿元）
- 折线图：持股股数变化（单位：百万股）
- 关键标注：
  ↗ 2024Q1：大幅加仓21.9%
  ⚡ 2024Q3：收益拐点，转为正收益
- 核心发现：市值斜率(0.12) > 股数斜率(0.08)，显示正收益表现
```

## 可视化建议模板

### 双轴图配置模板

```json
{
  "chart_type": "dual_axis",
  "title": "三花智控持仓市值与股数双轴历史图",
  "subtitle": "博时国证龙头家电ETF持仓分析",
  "data_source": "基金季度持仓报告",
  "axes": {
    "primary": {
      "title": "持仓市值（亿元）",
      "type": "bar",
      "color": "#4A90E2",
      "y_axis_position": "left"
    },
    "secondary": {
      "title": "持股股数（百万股）",
      "type": "line",
      "color": "#E24A4A",
      "y_axis_position": "right"
    }
  },
  "annotations": [
    {
      "quarter": "2024Q1",
      "text": "大幅加仓21.9%",
      "type": "increase",
      "color": "#4CAF50"
    },
    {
      "quarter": "2024Q3",
      "text": "收益拐点",
      "type": "turning_point",
      "color": "#FF9800"
    }
  ],
  "trend_lines": [
    {
      "type": "market_value_trend",
      "color": "#4A90E2",
      "style": "dashed"
    },
    {
      "type": "shares_trend",
      "color": "#E24A4A",
      "style": "dashed"
    }
  ],
  "display_options": {
    "show_grid": true,
    "show_legend": true,
    "show_data_labels": false,
    "responsive": true
  }
}
```

### 颜色方案模板

```json
{
  "color_schemes": {
    "profit_positive": {
      "primary_color": "#4CAF50",  // 绿色
      "secondary_color": "#8BC34A",
      "accent_color": "#CDDC39",
      "background_color": "#F1F8E9"
    },
    "profit_negative": {
      "primary_color": "#F44336",  // 红色
      "secondary_color": "#E57373",
      "accent_color": "#EF9A9A",
      "background_color": "#FFEBEE"
    },
    "neutral": {
      "primary_color": "#2196F3",  // 蓝色
      "secondary_color": "#64B5F6",
      "accent_color": "#90CAF9",
      "background_color": "#E3F2FD"
    }
  },
  "annotation_colors": {
    "increase": "#4CAF50",     // 加仓：绿色
    "decrease": "#F44336",     // 减仓：红色
    "turning_point": "#FF9800", // 拐点：橙色
    "peak": "#9C27B0",         // 峰值：紫色
    "valley": "#00BCD4"        // 谷值：青色
  }
}
```

## SEO元数据模板

### 博客文章SEO模板

```yaml
title: "三花智控深度分析：大师如何在家电龙头股上赚取15.8%年化收益？"
meta_description: "基于博时国证龙头家电ETF持仓数据，深度分析三花智控(002050)的投资价值。揭示大师的收益密码：市值斜率>股数斜率，正收益4.2%。包含双轴图分析、操作节点解读和投资启示。"
keywords:
  - "三花智控"
  - "002050"
  - "基金持仓分析"
  - "双轴图"
  - "投资大师"
  - "家电ETF"
  - "持仓数据"
  - "收益分析"
slug: "sanhua-zhikong-fund-holding-analysis-2026"
author: "投资分析团队"
published_date: "2026-03-07"
modified_date: "2026-03-07"
category: "投资分析"
tags:
  - "基金分析"
  - "持仓数据"
  - "双轴图"
  - "收益分析"
  - "家电行业"
featured_image: "/images/sanhua-zhikong-dual-axis-chart.png"
reading_time: "8分钟"
word_count: 1850
```

### 结构化数据（JSON-LD）模板

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "三花智控深度分析：大师如何在家电龙头股上赚取15.8%年化收益？",
  "description": "基于博时国证龙头家电ETF持仓数据的深度分析报告",
  "image": "https://example.com/images/sanhua-zhikong-dual-axis-chart.png",
  "author": {
    "@type": "Organization",
    "name": "投资分析团队"
  },
  "publisher": {
    "@type": "Organization",
    "name": "投资分析平台",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "datePublished": "2026-03-07",
  "dateModified": "2026-03-07",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/articles/sanhua-zhikong-analysis"
  },
  "articleSection": "投资分析",
  "keywords": "三花智控,002050,基金持仓分析,双轴图,投资大师",
  "wordCount": 1850,
  "timeRequired": "PT8M"
}
```

## 输出文件结构示例

```
reports/
├── 159730_analysis_20260307.json          # 完整JSON报告
├── 159730_summary_20260307.txt            # 自然语言总结
├── 159730_executive_summary_20260307.md   # 执行摘要
└── csv_data/
    ├── 002050_159730_dual_axis.csv        # 个股CSV数据
    ├── 000651_159730_dual_axis.csv
    ├── 000333_159730_dual_axis.csv
    └── all_stocks_159730_dual_axis.csv    # 合并CSV数据

blog_content/
├── 159730_blog_outline_7segment.md        # 7段式博客大纲
├── 159730_chart_captions.json             # 图表说明文字
├── 159730_seo_metadata.yaml               # SEO元数据
└── visualization/
    ├── 159730_color_scheme.json           # 颜色方案
    └── 159730_chart_configs.json          # 图表配置
```

## 模板使用指南

### 1. 选择适合的模板

| 使用场景 | 推荐模板 | 输出格式 |
|---------|----------|----------|
| 完整分析报告 | 完整JSON报告模板 | JSON |
| 快速查看结果 | 简化报告模板 | JSON |
| 生成可视化数据 | 双轴图CSV模板 | CSV |
| 写作内容支持 | 自然语言总结模板 | Markdown |
| 博客内容规划 | 7段式博客大纲模板 | Markdown |
| SEO优化 | SEO元数据模板 | YAML/JSON |

### 2. 自定义模板变量

所有模板支持以下变量替换：

| 变量 | 描述 | 示例 |
|------|------|------|
| `{fund_code}` | 基金代码 | 159730 |
| `{fund_name}` | 基金名称 | 博时国证龙头家电ETF |
| `{analysis_date}` | 分析日期 | 2026-03-07 |
| `{stock_code}` | 股票代码 | 002050 |
| `{stock_name}` | 股票名称 | 三花智控 |
| `{quarter}` | 季度 | 2024Q1 |
| `{change_pct}` | 变化百分比 | 21.9 |

### 3. 模板扩展建议

1. **添加自定义字段**：根据具体需求扩展JSON结构
2. **本地化调整**：调整语言风格和目标读者
3. **品牌一致性**：添加品牌颜色和标识
4. **格式优化**：调整输出格式以适应不同平台

## 质量检查清单

使用模板前，请检查：

- [ ] 所有变量已正确替换
- [ ] 数据一致性（如日期格式统一）
- [ ] 文件路径和命名规范
- [ ] 敏感信息已脱敏
- [ ] 符合目标平台的格式要求
- [ ] 包含必要的元数据和文档