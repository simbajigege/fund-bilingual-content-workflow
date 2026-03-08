# 分析算法详解

本文档详细说明基金持仓热力图数据的分析算法和逻辑。

## 1. 热力图信号识别算法

### 1.1 信号分类标准

#### 权重阈值定义
- **大色块**：`weight` > 5% （前20%的重仓股）
- **中色块**：2% ≤ `weight` ≤ 5%
- **小色块**：`weight` < 2%

#### AI评级分类
- **绿色（看好）**：`action` ∈ ["强力买入", "买入"]
- **黄色（中性）**：`action` = "持有"
- **红色（看空）**：`action` ∈ ["卖出", "强力卖出"]

### 1.2 关键信号识别

```python
def identify_heatmap_signals(stocks):
    signals = {
        "strong_buy_heavy": [],  # 大色块+绿色
        "strong_sell_heavy": [], # 大色块+红色
        "strong_buy_light": [],  # 小色块+绿色
        "neutral_heavy": [],     # 大色块+黄色
        "neutral_light": [],     # 小色块+黄色
        "strong_sell_light": []  # 小色块+红色
    }

    for stock in stocks:
        weight = stock["weight"]
        action = stock["analysis_summary"]["action"]

        # 确定权重级别
        if weight > 5:
            weight_level = "heavy"
        elif weight < 2:
            weight_level = "light"
        else:
            weight_level = "medium"

        # 确定颜色级别
        if action in ["强力买入", "买入"]:
            color = "green"
        elif action == "持有":
            color = "yellow"
        else:
            color = "red"

        # 分类信号
        signal_key = f"{color}_{weight_level}"
        if signal_key in ["green_heavy", "red_heavy", "green_light"]:
            signals[signal_key].append(stock)

    return signals
```

### 1.3 整体颜色分析

```python
def analyze_overall_color(stocks):
    total = len(stocks)
    if total == 0:
        return {"is_red": False, "red_percentage": 0}

    # 统计红色评级比例
    red_count = 0
    for stock in stocks:
        action = stock["analysis_summary"]["action"]
        if action in ["卖出", "强力卖出"]:
            red_count += 1

    red_percentage = (red_count / total) * 100

    # 判断整体是否偏红
    is_red = red_percentage > 30  # 超过30%为红色评级

    return {
        "is_red": is_red,
        "red_percentage": red_percentage,
        "red_count": red_count,
        "total_count": total
    }
```

## 2. 财务指标分析算法

### 2.1 估值分析

```python
def analyze_valuation(stocks):
    pe_ratios = [s["pe_ratio"] for s in stocks if s["pe_ratio"]]
    pb_ratios = [s["pb_ratio"] for s in stocks if s["pb_ratio"]]

    # 分位数分析
    def calculate_percentiles(values):
        if not values:
            return None
        sorted_vals = sorted(values)
        return {
            "min": min(values),
            "p25": sorted_vals[len(values)//4],
            "median": sorted_vals[len(values)//2],
            "p75": sorted_vals[3*len(values)//4],
            "max": max(values),
            "count": len(values)
        }

    return {
        "pe_stats": calculate_percentiles(pe_ratios),
        "pb_stats": calculate_percentiles(pb_ratios),
        "low_pe_stocks": [s for s in stocks if s.get("pe_ratio", float('inf')) < 15],
        "low_pb_stocks": [s for s in stocks if s.get("pb_ratio", float('inf')) < 1.5]
    }
```

### 2.2 价格动量分析

```python
def analyze_momentum(stocks):
    # 涨跌幅分析
    changes = [s["change_pct"] for s in stocks]
    amplitudes = [s["amplitude"] for s in stocks]

    # 强势股识别（涨幅大、振幅适中）
    strong_stocks = []
    for stock in stocks:
        change = stock["change_pct"]
        amplitude = stock["amplitude"]

        # 强势股条件
        if change > 2.0 and 2.0 < amplitude < 8.0:
            strong_stocks.append({
                "stock_code": stock["stock_code"],
                "stock_name": stock["stock_name"],
                "change_pct": change,
                "amplitude": amplitude,
                "weight": stock["weight"]
            })

    return {
        "avg_change": sum(changes)/len(changes) if changes else 0,
        "max_change": max(changes) if changes else 0,
        "min_change": min(changes) if changes else 0,
        "avg_amplitude": sum(amplitudes)/len(amplitudes) if amplitudes else 0,
        "strong_stocks": sorted(strong_stocks, key=lambda x: x["change_pct"], reverse=True)[:5]
    }
```

### 2.3 流动性分析

```python
def analyze_liquidity(stocks):
    turnover_rates = [s["turnover_rate"] for s in stocks]
    volumes = [s["volume"] for s in stocks]

    # 高流动性股票识别
    high_liquidity = []
    for stock in stocks:
        turnover = stock["turnover_rate"]
        volume = stock["volume"]

        if turnover > 3.0 or volume > 10000000:  # 换手率>3%或成交量>1000万股
            high_liquidity.append({
                "stock_code": stock["stock_code"],
                "stock_name": stock["stock_name"],
                "turnover_rate": turnover,
                "volume": volume,
                "weight": stock["weight"]
            })

    return {
        "avg_turnover": sum(turnover_rates)/len(turnover_rates) if turnover_rates else 0,
        "high_liquidity_stocks": sorted(high_liquidity, key=lambda x: x["turnover_rate"], reverse=True)[:5],
        "total_volume": sum(volumes) if volumes else 0
    }
```

## 3. AI投资建议分析算法

### 3.1 操作建议分布

```python
def analyze_ai_actions(stocks):
    action_count = {
        "强力买入": 0,
        "买入": 0,
        "持有": 0,
        "卖出": 0,
        "强力卖出": 0
    }

    total_weight_by_action = {
        "强力买入": 0,
        "买入": 0,
        "持有": 0,
        "卖出": 0,
        "强力卖出": 0
    }

    for stock in stocks:
        action = stock["analysis_summary"]["action"]
        weight = stock["weight"]

        if action in action_count:
            action_count[action] += 1
            total_weight_by_action[action] += weight

    total_stocks = len(stocks)
    total_weight = sum(stock["weight"] for stock in stocks)

    return {
        "count_distribution": {k: v for k, v in action_count.items() if v > 0},
        "weight_distribution": {k: v for k, v in total_weight_by_action.items() if v > 0},
        "percentage_by_count": {k: (v/total_stocks*100) for k, v in action_count.items() if v > 0},
        "percentage_by_weight": {k: (v/total_weight*100) for k, v in total_weight_by_action.items() if v > 0}
    }
```

### 3.2 置信度与风险评估

```python
def analyze_confidence_risk(stocks):
    confidences = []
    risk_scores = []
    price_gaps = []  # 目标价与当前价差距百分比

    for stock in stocks:
        analysis = stock["analysis_summary"]
        confidences.append(analysis["confidence"])
        risk_scores.append(analysis["risk_score"])

        # 计算价格差距
        current_price = stock["current_price"]
        target_price = analysis["target_price"]
        if current_price > 0 and target_price > 0:
            gap_pct = ((target_price - current_price) / current_price) * 100
            price_gaps.append({
                "stock_code": stock["stock_code"],
                "stock_name": stock["stock_name"],
                "current_price": current_price,
                "target_price": target_price,
                "gap_pct": gap_pct,
                "weight": stock["weight"]
            })

    # 高置信度低风险股票
    high_confidence_low_risk = []
    for stock in stocks:
        analysis = stock["analysis_summary"]
        if analysis["confidence"] > 0.7 and analysis["risk_score"] < 0.4:
            high_confidence_low_risk.append({
                "stock_code": stock["stock_code"],
                "stock_name": stock["stock_name"],
                "confidence": analysis["confidence"],
                "risk_score": analysis["risk_score"],
                "action": analysis["action"],
                "weight": stock["weight"]
            })

    return {
        "avg_confidence": sum(confidences)/len(confidences) if confidences else 0,
        "avg_risk_score": sum(risk_scores)/len(risk_scores) if risk_scores else 0,
        "price_gaps": sorted(price_gaps, key=lambda x: x["gap_pct"], reverse=True)[:10],
        "high_confidence_low_risk_stocks": sorted(high_confidence_low_risk, key=lambda x: x["confidence"], reverse=True)
    }
```

## 4. 行业分布分析算法

```python
def analyze_industry_distribution(stocks):
    industry_stats = {}

    for stock in stocks:
        industry = stock["industry"]
        weight = stock["weight"]

        if industry not in industry_stats:
            industry_stats[industry] = {
                "count": 0,
                "total_weight": 0,
                "stocks": []
            }

        industry_stats[industry]["count"] += 1
        industry_stats[industry]["total_weight"] += weight
        industry_stats[industry]["stocks"].append({
            "stock_code": stock["stock_code"],
            "stock_name": stock["stock_name"],
            "weight": weight,
            "action": stock["analysis_summary"]["action"]
        })

    # 按权重排序
    sorted_industries = sorted(
        industry_stats.items(),
        key=lambda x: x[1]["total_weight"],
        reverse=True
    )

    # 计算百分比
    total_weight = sum(stats["total_weight"] for stats in industry_stats.values())
    for industry, stats in industry_stats.items():
        stats["weight_percentage"] = (stats["total_weight"] / total_weight * 100) if total_weight > 0 else 0

    return {
        "by_weight": dict(sorted_industries),
        "by_count": dict(sorted(industry_stats.items(), key=lambda x: x[1]["count"], reverse=True)),
        "top_industries": sorted_industries[:5]
    }
```

## 5. 综合评分算法

### 5.1 个股综合评分

```python
def calculate_stock_score(stock):
    """计算个股综合评分（0-100）"""
    score = 50  # 基础分

    # 1. AI建议权重（40%）
    action = stock["analysis_summary"]["action"]
    action_scores = {
        "强力买入": 90,
        "买入": 75,
        "持有": 50,
        "卖出": 25,
        "强力卖出": 10
    }
    action_score = action_scores.get(action, 50)

    # 2. 置信度调整（20%）
    confidence = stock["analysis_summary"]["confidence"]

    # 3. 风险调整（20%）
    risk_score = stock["analysis_summary"]["risk_score"]

    # 4. 估值调整（10%）
    pe_ratio = stock.get("pe_ratio")
    pe_score = 70 if pe_ratio and pe_ratio < 15 else 50

    # 5. 动量调整（10%）
    change_pct = stock["change_pct"]
    momentum_score = 60 if change_pct > 0 else 40

    # 加权计算
    final_score = (
        action_score * 0.4 +
        confidence * 100 * 0.2 +
        (1 - risk_score) * 100 * 0.2 +
        pe_score * 0.1 +
        momentum_score * 0.1
    )

    return min(100, max(0, final_score))
```

### 5.2 组合综合评分

```python
def calculate_portfolio_score(stocks, analysis_results):
    """计算基金持仓组合综合评分"""
    if not stocks:
        return 50

    scores = []
    weighted_scores = []

    for stock in stocks:
        score = calculate_stock_score(stock)
        weight = stock["weight"] / 100  # 转换为小数

        scores.append(score)
        weighted_scores.append(score * weight)

    # 等权平均分
    equal_weight_score = sum(scores) / len(scores)

    # 加权平均分
    total_weight = sum(stock["weight"] for stock in stocks) / 100
    weighted_avg_score = sum(weighted_scores) / total_weight if total_weight > 0 else equal_weight_score

    # 信号加分/减分
    signal_adjustment = 0
    if analysis_results["heatmap_signals"]["strong_buy_heavy"]:
        signal_adjustment += 5
    if analysis_results["heatmap_signals"]["strong_sell_heavy"]:
        signal_adjustment -= 3
    if analysis_results["overall_color"]["is_red"]:
        signal_adjustment -= 10

    final_score = weighted_avg_score + signal_adjustment

    return {
        "equal_weight_score": equal_weight_score,
        "weighted_avg_score": weighted_avg_score,
        "signal_adjustment": signal_adjustment,
        "final_score": min(100, max(0, final_score)),
        "score_interpretation": interpret_score(final_score)
    }

def interpret_score(score):
    """解释评分结果"""
    if score >= 80:
        return "优秀：持仓质量高，AI普遍看好"
    elif score >= 70:
        return "良好：持仓质量较好，有一定投资价值"
    elif score >= 60:
        return "一般：持仓质量中等，需谨慎选择"
    elif score >= 50:
        return "中等：持仓质量一般，存在一定风险"
    else:
        return "较差：持仓质量低，风险较高"
```

## 6. 自然语言总结生成算法

### 6.1 总结模板结构

```python
SUMMARY_TEMPLATE = """
【基金持仓分析报告 - {fund_code}】

一、持仓概况
{overview}

二、关键信号发现
{signals}

三、财务指标分析
{financial}

四、AI投资建议汇总
{ai_advice}

五、行业分布特征
{industry}

六、综合评估
{assessment}

七、投资建议
{recommendation}

报告生成时间：{timestamp}
数据来源：ai2alpha.cn
"""

def generate_summary(analysis_results, fund_code):
    """生成自然语言分析总结"""
    return SUMMARY_TEMPLATE.format(
        fund_code=fund_code,
        overview=generate_overview(analysis_results),
        signals=generate_signals_summary(analysis_results),
        financial=generate_financial_summary(analysis_results),
        ai_advice=generate_ai_advice_summary(analysis_results),
        industry=generate_industry_summary(analysis_results),
        assessment=generate_assessment_summary(analysis_results),
        recommendation=generate_recommendation(analysis_results),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
```

### 6.2 各模块生成函数

```python
def generate_overview(results):
    """生成概况总结"""
    metadata = results["metadata"]
    total_stocks = metadata["total_stocks"]
    total_value = metadata.get("total_market_value", 0)

    return f"本次分析涵盖{total_stocks}只持仓股票。总持仓市值约{format_money(total_value)}。"

def generate_signals_summary(results):
    """生成信号总结"""
    signals = results["heatmap_signals"]
    overall = results["overall_color"]

    summary_parts = []

    # 关键信号
    if signals["strong_buy_heavy"]:
        count = len(signals["strong_buy_heavy"])
        names = [s["stock_name"] for s in signals["strong_buy_heavy"][:3]]
        summary_parts.append(f"发现{count}只'重仓且AI看好'股票，包括{', '.join(names)}等")

    if signals["strong_sell_heavy"]:
        count = len(signals["strong_sell_heavy"])
        names = [s["stock_name"] for s in signals["strong_sell_heavy"][:3]]
        summary_parts.append(f"发现{count}只'重仓但AI看空'股票，包括{', '.join(names)}，存在明显分歧")

    # 整体颜色
    if overall["is_red"]:
        summary_parts.append(f"整体持仓偏红，{overall['red_percentage']:.1f}%的股票被AI评为卖出或强力卖出，需谨慎对待")

    return "；".join(summary_parts) if summary_parts else "未发现显著关键信号。"

def format_money(value):
    """格式化金额"""
    if value >= 1e8:
        return f"{value/1e8:.2f}亿元"
    elif value >= 1e4:
        return f"{value/1e4:.2f}万元"
    else:
        return f"{value:.2f}元"
```

## 7. 性能优化建议

### 7.1 缓存策略
- 对API返回数据缓存15分钟
- 对分析结果缓存5分钟
- 使用基金代码作为缓存键

### 7.2 批量处理
- 支持批量分析多个基金
- 异步处理大量数据
- 增量更新分析结果

### 7.3 内存优化
- 流式处理大型数据集
- 使用生成器避免一次性加载
- 及时释放不再使用的数据