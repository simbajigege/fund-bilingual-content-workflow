# 输出模板示例

本文档提供结构化报告和自然语言总结的输出模板示例。

## 1. 结构化JSON报告模板

### 完整报告结构

```json
{
  "metadata": {
    "fund_code": "159730",
    "fund_name": "国联安中证全指证券公司ETF",
    "analysis_date": "2026-03-07T14:30:00",
    "data_source": "ai2alpha.cn",
    "data_collection_time": "2026-03-06T15:14:06.323010",
    "total_stocks": 10,
    "total_market_value": 12345678900,
    "analysis_version": "1.0.0"
  },
  "heatmap_signals": {
    "strong_buy_heavy": [
      {
        "stock_code": "002508",
        "stock_name": "老板电器",
        "weight": 2.59,
        "ai_rating": "Buy",
        "ai_score": 72.5,
        "current_price": 20.44,
        "change_pct": 2.149,
        "pe_ratio": 12.24,
        "action": "持有",
        "confidence": 0.6,
        "target_price": 23,
        "upside_potential": 12.5
      }
    ],
    "strong_sell_heavy": [],
    "strong_buy_light": [
      {
        "stock_code": "000921",
        "stock_name": "海信家电",
        "weight": 1.25,
        "ai_rating": "Buy",
        "ai_score": 68.3,
        "current_price": 23.15,
        "change_pct": 1.313,
        "pe_ratio": 9.411,
        "action": "持有",
        "confidence": 0.7,
        "target_price": 30,
        "upside_potential": 29.6
      }
    ],
    "neutral_heavy": [],
    "neutral_light": [],
    "strong_sell_light": []
  },
  "overall_color": {
    "is_red": false,
    "red_percentage": 10.0,
    "red_count": 1,
    "total_count": 10,
    "color_interpretation": "整体持仓偏中性，AI看空比例较低"
  },
  "financial_analysis": {
    "valuation_summary": {
      "pe_stats": {
        "min": 8.5,
        "p25": 10.2,
        "median": 12.8,
        "p75": 15.3,
        "max": 22.1,
        "count": 10,
        "avg": 13.2
      },
      "pb_stats": {
        "min": 1.2,
        "p25": 1.5,
        "median": 1.8,
        "p75": 2.1,
        "max": 2.8,
        "count": 10,
        "avg": 1.9
      },
      "low_pe_stocks": [
        {
          "stock_code": "000921",
          "stock_name": "海信家电",
          "pe_ratio": 9.411,
          "weight": 1.25,
          "percentile": 20
        }
      ],
      "low_pb_stocks": [
        {
          "stock_code": "002508",
          "stock_name": "老板电器",
          "pb_ratio": 1.692,
          "weight": 2.59,
          "percentile": 40
        }
      ]
    },
    "momentum_summary": {
      "avg_change": 1.85,
      "max_change": 3.2,
      "min_change": -0.5,
      "avg_amplitude": 3.8,
      "strong_stocks": [
        {
          "stock_code": "002508",
          "stock_name": "老板电器",
          "change_pct": 2.149,
          "amplitude": 3.998,
          "weight": 2.59,
          "momentum_score": 85
        }
      ]
    },
    "liquidity_summary": {
      "avg_turnover": 2.5,
      "total_volume": 45678900,
      "high_liquidity_stocks": [
        {
          "stock_code": "002508",
          "stock_name": "老板电器",
          "turnover_rate": 0.6746,
          "volume": 6297316,
          "weight": 2.59,
          "liquidity_score": 75
        }
      ]
    }
  },
  "ai_advice_summary": {
    "action_distribution": {
      "count": {
        "持有": 8,
        "买入": 2,
        "卖出": 0,
        "强力买入": 0,
        "强力卖出": 0
      },
      "weight": {
        "持有": 78.5,
        "买入": 21.5,
        "卖出": 0,
        "强力买入": 0,
        "强力卖出": 0
      }
    },
    "confidence_stats": {
      "avg_confidence": 0.65,
      "min_confidence": 0.5,
      "max_confidence": 0.8,
      "high_confidence_stocks": [
        {
          "stock_code": "000921",
          "stock_name": "海信家电",
          "confidence": 0.7,
          "action": "持有",
          "weight": 1.25
        }
      ]
    },
    "risk_stats": {
      "avg_risk_score": 0.55,
      "min_risk_score": 0.4,
      "max_risk_score": 0.7,
      "low_risk_stocks": [
        {
          "stock_code": "002508",
          "stock_name": "老板电器",
          "risk_score": 0.6,
          "action": "持有",
          "weight": 2.59
        }
      ]
    },
    "price_gap_analysis": {
      "avg_upside_potential": 15.2,
      "max_upside_potential": 29.6,
      "high_potential_stocks": [
        {
          "stock_code": "000921",
          "stock_name": "海信家电",
          "current_price": 23.15,
          "target_price": 30,
          "upside_potential": 29.6,
          "weight": 1.25,
          "confidence": 0.7
        }
      ]
    }
  },
  "industry_distribution": {
    "by_weight": {
      "家电行业": {
        "count": 2,
        "total_weight": 3.84,
        "weight_percentage": 38.4,
        "stocks": [
          {
            "stock_code": "002508",
            "stock_name": "老板电器",
            "weight": 2.59,
            "action": "持有"
          },
          {
            "stock_code": "000921",
            "stock_name": "海信家电",
            "weight": 1.25,
            "action": "持有"
          }
        ]
      }
    },
    "top_industries": [
      {
        "industry": "家电行业",
        "weight_percentage": 38.4,
        "count": 2,
        "representative_stocks": ["老板电器", "海信家电"]
      }
    ]
  },
  "portfolio_score": {
    "equal_weight_score": 68.5,
    "weighted_avg_score": 72.3,
    "signal_adjustment": 5,
    "final_score": 77.3,
    "score_interpretation": "良好：持仓质量较好，有一定投资价值",
    "score_components": {
      "ai_advice_score": 75,
      "valuation_score": 70,
      "momentum_score": 80,
      "liquidity_score": 75
    }
  },
  "top_signals": [
    {
      "type": "strong_buy_heavy",
      "stock_code": "002508",
      "stock_name": "老板电器",
      "description": "重仓且AI看好，权重2.59%，AI评级'Buy'",
      "priority": "high"
    },
    {
      "type": "high_upside_potential",
      "stock_code": "000921",
      "stock_name": "海信家电",
      "description": "目标价上涨空间29.6%，置信度0.7",
      "priority": "medium"
    }
  ],
  "recommendations": {
    "immediate_actions": [
      "重点分析'老板电器'，关注其重仓且AI看好的逻辑",
      "跟踪'海信家电'的目标价达成情况"
    ],
    "watch_list": [
      {
        "stock_code": "002508",
        "stock_name": "老板电器",
        "reason": "重仓+AI看好双重信号",
        "monitoring_points": ["Q1财报业绩", "智能厨电转型进展"]
      }
    ],
    "risk_warnings": [
      "整体持仓AI置信度一般（平均0.65），建议结合其他分析",
      "部分股票风险评分较高，需注意仓位控制"
    ]
  }
}
```

## 2. 自然语言总结模板

### 完整总结模板

```
【基金持仓分析报告 - {fund_code}】

一、持仓概况
本次分析涵盖{total_stocks}只持仓股票，总持仓市值约{total_value}。数据采集时间：{collection_time}。

二、关键信号发现
{signals_summary}

三、财务指标分析
1. 估值水平：平均PE {avg_pe}倍，PB {avg_pb}倍，{valuation_comment}
2. 价格动量：平均涨幅{avg_change}%，{momentum_comment}
3. 流动性：平均换手率{avg_turnover}%，{liquidity_comment}

四、AI投资建议汇总
1. 操作建议分布：{action_distribution}
2. 平均置信度：{avg_confidence}，{confidence_comment}
3. 目标价空间：平均上涨潜力{avg_upside}%，最高{max_upside}%
4. 风险评估：平均风险评分{avg_risk}，{risk_comment}

五、行业分布特征
{industry_summary}

六、综合评估
组合综合评分：{final_score}/100 ({score_interpretation})
{assessment_details}

七、投资建议
1. 重点关注：{focus_stocks}
2. 风险提示：{risk_warnings}
3. 后续跟踪：{follow_up}

报告生成时间：{timestamp}
数据来源：ai2alpha.cn
```

### 各模块填充示例

#### 信号总结模块
```
发现2只'重仓且AI看好'股票，包括老板电器、海信家电等，权重合计5.2%；
发现1只'重仓但AI看空'股票（中国平安），存在明显分歧；
整体持仓偏中性，20%的股票被AI评为卖出或强力卖出。
```

#### 财务分析模块
```
1. 估值水平：平均PE 13.2倍，PB 1.9倍，估值处于合理区间，部分家电股估值较低；
2. 价格动量：平均涨幅1.85%，老板电器涨幅领先（2.15%）；
3. 流动性：平均换手率2.5%，流动性适中，适合中长期持有。
```

#### AI建议汇总模块
```
1. 操作建议分布：80%建议持有，20%建议买入，无卖出建议；
2. 平均置信度：0.65，AI判断把握度中等；
3. 目标价空间：平均上涨潜力15.2%，海信家电空间最大（29.6%）；
4. 风险评估：平均风险评分0.55，风险控制尚可。
```

#### 行业分布模块
```
持仓集中在3个行业：家电（38.4%）、金融（25.2%）、医药（18.6%）；
家电行业占比最高，包含老板电器、海信家电等龙头公司。
```

#### 综合评估模块
```
组合综合评分：77.3/100（良好：持仓质量较好，有一定投资价值）
优势：AI普遍看好，估值合理，行业分布均衡；
不足：整体置信度一般，部分股票风险评分较高。
```

#### 投资建议模块
```
1. 重点关注：老板电器（重仓+AI看好）、海信家电（高上涨潜力）；
2. 风险提示：注意整体持仓AI置信度一般，建议结合基本面分析；
3. 后续跟踪：关注家电行业政策变化，跟踪目标价达成情况。
```

## 3. 内容生产工作流模板

### 博客结构模板（7段式）

```
# 标题：{基金名称}持仓分析：{关键发现}的投资启示

## 1. 开篇：热力图全景一览
[插入持仓热力图截图]
说明：色块大小代表仓位权重，颜色代表AI综合评级
读者引导：点击图片→跳转工具页面查看实时数据

## 2. 关键信号解读：大师与AI的共识与分歧
- 共识点：{共识股票}为何同时获得重仓和AI看好？
- 分歧点：{分歧股票}的重仓逻辑与AI看空原因分析

## 3. 财务指标深度分析
- 估值分析：PE/PB分位数，哪些股票被低估？
- 动量分析：涨幅与振幅，谁在强势上升通道？
- 流动性：换手率与成交量，机构关注度如何？

## 4. AI投资建议汇总
- 操作建议分布：持有/买入/卖出比例
- 置信度分析：AI判断的把握度如何？
- 目标价空间：哪些股票上涨潜力最大？

## 5. 行业分布与赛道选择
- 行业集中度：大师重点布局哪些赛道？
- 细分龙头：各行业中的代表性公司
- 趋势判断：行业配置背后的逻辑

## 6. 综合评估与风险评估
- 组合评分：{分数}/100，整体质量评估
- 优势与不足：持仓的核心亮点与潜在风险
- 风险控制：需要注意的关键风险点

## 7. 投资建议与行动指南
- 重点关注：{重点股票}的跟踪要点
- 操作建议：适合的投资者类型与策略
- 后续跟踪：需要关注的关键指标和时间点

## 附录：数据来源与方法说明
- 数据来源：ai2alpha.cn基金持仓热力图
- 分析时间：{分析日期}
- 免责声明：本文为数据分析，不构成投资建议
```

### 社交媒体摘要模板

```
🔥 {基金名称}持仓分析快报 🔥

📊 关键发现：
- 重仓+AI看好：{股票1}、{股票2}
- 重仓但AI看空：{股票3}（分歧点！）
- 整体评分：{分数}/100

💡 投资启示：
1. {启示1}
2. {启示2}
3. {启示3}

📈 重点关注：{重点股票}
⚠️ 风险提示：{主要风险}

#基金分析 #投资研究 #AI选股 #{基金代码}
```

## 4. API响应模板

### 成功响应模板

```json
{
  "success": true,
  "fund_code": "159730",
  "analysis": {
    // 完整分析结果
  },
  "summary": "自然语言总结文本",
  "metadata": {
    "analysis_time": "2026-03-07T14:30:00",
    "data_source": "ai2alpha.cn",
    "processing_time_ms": 450
  }
}
```

### 错误响应模板

```json
{
  "success": false,
  "error": {
    "code": "API_ERROR",
    "message": "无法获取基金数据",
    "details": "API返回错误：HTTP 404"
  },
  "suggestions": [
    "检查基金代码是否正确",
    "确认网络连接正常",
    "稍后重试"
  ]
}
```

## 5. 配置文件模板

### 分析配置模板（config.yaml）

```yaml
# 热力图信号阈值配置
heatmap_thresholds:
  heavy_weight: 5.0    # 大色块阈值（%）
  light_weight: 2.0    # 小色块阈值（%）
  red_percentage: 30.0 # 整体偏红阈值（%）

# 财务指标阈值配置
financial_thresholds:
  low_pe: 15.0         # 低PE阈值
  low_pb: 1.5          # 低PB阈值
  high_turnover: 3.0   # 高换手率阈值（%）
  strong_change: 2.0   # 强势涨幅阈值（%）

# AI建议权重配置
ai_weighting:
  action: 0.4          # 操作建议权重
  confidence: 0.2      # 置信度权重
  risk: 0.2            # 风险评分权重
  valuation: 0.1       # 估值权重
  momentum: 0.1        # 动量权重

# 输出配置
output:
  json_indent: 2       # JSON缩进空格数
  summary_language: "zh-CN" # 总结语言
  include_raw_data: false   # 是否包含原始数据

# API配置
api:
  base_url: "https://ai2alpha.cn/api/v1"
  timeout: 30          # 超时时间（秒）
  retry_attempts: 3    # 重试次数
```

## 6. 数据验证模板

### 数据完整性检查

```python
def validate_data(data):
    """验证数据完整性"""
    required_fields = [
        "success",
        "data",
        "meta"
    ]

    required_stock_fields = [
        "stock_code",
        "stock_name",
        "weight",
        "current_price",
        "analysis_summary"
    ]

    required_analysis_fields = [
        "action",
        "target_price",
        "confidence",
        "risk_score"
    ]

    # 检查顶层字段
    for field in required_fields:
        if field not in data:
            return False, f"Missing top-level field: {field}"

    # 检查股票数据
    for stock in data.get("data", []):
        for field in required_stock_fields:
            if field not in stock:
                return False, f"Missing stock field {field} in {stock.get('stock_code', 'unknown')}"

        # 检查分析摘要
        analysis = stock.get("analysis_summary", {})
        for field in required_analysis_fields:
            if field not in analysis:
                return False, f"Missing analysis field {field} in {stock.get('stock_code', 'unknown')}"

    return True, "Data validation passed"
```

## 7. 性能监控模板

### 分析性能报告

```json
{
  "performance_metrics": {
    "data_fetch_time_ms": 320,
    "analysis_time_ms": 450,
    "total_time_ms": 770,
    "memory_usage_mb": 45.2,
    "cpu_usage_percent": 12.5,
    "stocks_processed": 10,
    "analysis_steps": [
      {
        "step": "data_validation",
        "time_ms": 15
      },
      {
        "step": "heatmap_analysis",
        "time_ms": 85
      },
      {
        "step": "financial_analysis",
        "time_ms": 120
      },
      {
        "step": "ai_advice_analysis",
        "time_ms": 95
      },
      {
        "step": "summary_generation",
        "time_ms": 135
      }
    ]
  },
  "resource_usage": {
    "peak_memory_mb": 52.1,
    "average_cpu_percent": 10.8,
    "disk_io_mb": 2.3
  }
}
```