# 分析算法详解

本文档详细说明基金个股持仓双轴历史图分析中使用的各种算法和计算逻辑。

## 目录

1. [个股精选算法](#个股精选算法)
2. [斜率计算方法](#斜率计算方法)
3. [收益分析算法](#收益分析算法)
4. [操作节点识别](#操作节点识别)
5. [趋势检测算法](#趋势检测算法)
6. [数据预处理](#数据预处理)
7. [权重计算](#权重计算)
8. [异常值处理](#异常值处理)

## 个股精选算法

### 精选评分体系

精选评分基于五个维度，每个维度有相应权重：

| 维度 | 权重 | 计算方法 | 评分范围 |
|------|------|----------|----------|
| 持仓权重 | 30% | 平均权重得分 | 0-100 |
| 持仓稳定性 | 25% | 持仓季度比例得分 | 0-100 |
| 权重变化趋势 | 20% | 权重斜率得分 | -100 到 100 |
| 收益表现 | 15% | 收益斜率得分 | -100 到 100 |
| 行业代表性 | 10% | 行业排名得分 | 0-100 |

### 1. 持仓权重得分计算

```python
def calculate_weight_score(avg_weight, min_threshold=3.0, max_threshold=20.0):
    """
    计算持仓权重得分
    avg_weight: 平均权重（%）
    min_threshold: 最低阈值，低于此值得0分
    max_threshold: 最高阈值，高于此值得100分
    """
    if avg_weight < min_threshold:
        return 0
    elif avg_weight > max_threshold:
        return 100
    else:
        # 线性插值
        return ((avg_weight - min_threshold) / (max_threshold - min_threshold)) * 100
```

### 2. 持仓稳定性得分计算

```python
def calculate_stability_score(quarters_held, total_quarters, min_ratio=0.7):
    """
    计算持仓稳定性得分
    quarters_held: 持仓季度数
    total_quarters: 总季度数
    min_ratio: 最低比例阈值，低于此值得0分
    """
    ratio = quarters_held / total_quarters

    if ratio < min_ratio:
        return 0
    else:
        # 线性映射：min_ratio → 0分，1.0 → 100分
        return ((ratio - min_ratio) / (1.0 - min_ratio)) * 100
```

### 3. 权重变化趋势得分计算

```python
def calculate_trend_score(weight_slope, min_slope=0.01):
    """
    计算权重变化趋势得分
    weight_slope: 权重时间序列的斜率（每季度变化百分比）
    min_slope: 最小有效斜率
    """
    if weight_slope > min_slope:
        # 正趋势：0-100分
        return min(100, (weight_slope / (min_slope * 5)) * 100)
    elif weight_slope < -min_slope:
        # 负趋势：-100-0分
        return max(-100, (weight_slope / (min_slope * 5)) * 100)
    else:
        # 无明显趋势：0分
        return 0
```

### 4. 收益表现得分计算

```python
def calculate_profit_score(market_value_slope, shares_slope):
    """
    计算收益表现得分
    market_value_slope: 市值曲线斜率
    shares_slope: 股数曲线斜率
    """
    # 核心判断：市值斜率 > 股数斜率 → 正收益
    profit_differential = market_value_slope - shares_slope

    if profit_differential > 0:
        # 正收益：0-100分
        return min(100, profit_differential * 1000)  # 调整缩放因子
    else:
        # 负收益：-100-0分
        return max(-100, profit_differential * 1000)
```

### 5. 行业代表性得分计算

```python
def calculate_industry_score(industry_rank, total_industries):
    """
    计算行业代表性得分
    industry_rank: 在该行业中的排名（1-based）
    total_industries: 总行业数
    """
    if industry_rank == 1:
        return 100  # 行业龙头
    elif industry_rank <= 3:
        return 80   # 行业前三
    elif industry_rank <= 5:
        return 60   # 行业前五
    elif industry_rank <= 10:
        return 40   # 行业前十
    else:
        return 20   # 其他
```

### 综合评分计算

```python
def calculate_comprehensive_score(scores, weights):
    """
    计算综合评分
    scores: 各维度得分字典
    weights: 各维度权重字典
    """
    total_score = 0
    total_weight = 0

    for dimension in scores:
        dimension_score = scores[dimension]
        dimension_weight = weights[dimension]

        # 归一化：将-100到100的得分映射到0-100
        if dimension_score < 0:
            normalized_score = 50 + (dimension_score / 2)  # -100 → 0, 0 → 50
        else:
            normalized_score = 50 + (dimension_score / 2)  # 0 → 50, 100 → 100

        total_score += normalized_score * dimension_weight
        total_weight += dimension_weight

    return total_score / total_weight if total_weight > 0 else 0
```

## 斜率计算方法

### 1. 线性回归法（推荐）

使用最小二乘法计算时间序列的线性趋势斜率。

```python
import numpy as np

def calculate_slope_linear_regression(y_values, x_values=None):
    """
    使用线性回归计算斜率
    y_values: 因变量数组
    x_values: 自变量数组（可选，默认为[0, 1, 2, ...]）
    """
    n = len(y_values)

    if n < 2:
        return 0

    if x_values is None:
        x_values = np.arange(n)

    # 计算均值
    x_mean = np.mean(x_values)
    y_mean = np.mean(y_values)

    # 计算斜率和截距
    numerator = np.sum((x_values - x_mean) * (y_values - y_mean))
    denominator = np.sum((x_values - x_mean) ** 2)

    if denominator == 0:
        return 0

    slope = numerator / denominator
    return slope
```

### 2. 简单斜率法

计算首尾点的斜率。

```python
def calculate_slope_simple(y_values):
    """
    使用简单方法计算斜率
    y_values: 数值数组
    """
    n = len(y_values)

    if n < 2:
        return 0

    # 计算首尾点的斜率
    slope = (y_values[-1] - y_values[0]) / (n - 1)
    return slope
```

### 3. 加权斜率法

给近期数据更高权重。

```python
def calculate_slope_weighted(y_values):
    """
    使用加权方法计算斜率（近期数据权重更高）
    y_values: 数值数组
    """
    n = len(y_values)

    if n < 2:
        return 0

    # 创建权重数组（线性递增）
    weights = np.arange(1, n + 1)

    # 加权线性回归
    x_values = np.arange(n)

    # 加权均值
    weighted_mean_x = np.average(x_values, weights=weights)
    weighted_mean_y = np.average(y_values, weights=weights)

    # 计算加权斜率
    numerator = np.sum(weights * (x_values - weighted_mean_x) * (y_values - weighted_mean_y))
    denominator = np.sum(weights * (x_values - weighted_mean_x) ** 2)

    if denominator == 0:
        return 0

    slope = numerator / denominator
    return slope
```

## 收益分析算法

### 1. 收益类型判断

基于市值斜率和股数斜率的相对关系判断收益类型。

```python
def analyze_profit_type(market_value_slope, shares_slope, threshold=0.01):
    """
    分析收益类型
    threshold: 斜率差异阈值
    """
    diff = market_value_slope - shares_slope

    if diff > threshold:
        return "positive_profit"  # 正收益
    elif diff < -threshold:
        return "negative_profit"  # 负收益
    else:
        return "neutral"  # 中性
```

### 2. 收益强度计算

```python
def calculate_profit_strength(market_value_slope, shares_slope):
    """
    计算收益强度
    """
    # 收益强度 = 市值斜率 - 股数斜率
    profit_strength = market_value_slope - shares_slope

    # 分类
    if profit_strength > 0.15:
        return "high_positive"  # 高正收益
    elif profit_strength > 0.05:
        return "moderate_positive"  # 中等正收益
    elif profit_strength > 0.01:
        return "low_positive"  # 低正收益
    elif profit_strength > -0.01:
        return "neutral"  # 中性
    elif profit_strength > -0.05:
        return "low_negative"  # 低负收益
    elif profit_strength > -0.15:
        return "moderate_negative"  # 中等负收益
    else:
        return "high_negative"  # 高负收益
```

### 3. 收益贡献度分析

```python
def analyze_profit_contribution(market_value_changes, shares_changes):
    """
    分析收益贡献度
    分解市值变化为：股价变化贡献 + 股数变化贡献
    """
    # 假设：市值变化 ≈ 股价变化 + 股数变化
    # 实际计算需要股价数据，这里使用简化模型

    contributions = []

    for i in range(1, len(market_value_changes)):
        mv_change = market_value_changes[i] - market_value_changes[i-1]
        shares_change = shares_changes[i] - shares_changes[i-1]

        # 简化模型：假设市值变化由两部分组成
        # 实际应用中需要股价数据来计算精确贡献
        price_contribution = mv_change - shares_change
        shares_contribution = shares_change

        contributions.append({
            "period": i,
            "total_change": mv_change,
            "price_contribution": price_contribution,
            "shares_contribution": shares_contribution,
            "price_contribution_pct": price_contribution / abs(mv_change) if mv_change != 0 else 0,
            "shares_contribution_pct": shares_contribution / abs(mv_change) if mv_change != 0 else 0
        })

    return contributions
```

## 操作节点识别

### 1. 大幅加仓/减仓检测

```python
def detect_significant_changes(shares_series, threshold=0.2):
    """
    检测大幅加仓/减仓
    shares_series: 股数时间序列
    threshold: 变化阈值（20%）
    """
    significant_changes = []

    for i in range(1, len(shares_series)):
        current = shares_series[i]
        previous = shares_series[i-1]

        if previous == 0:
            continue

        change_pct = (current - previous) / abs(previous)

        if abs(change_pct) >= threshold:
            change_type = "increase" if change_pct > 0 else "decrease"
            significant_changes.append({
                "period": i,
                "from": previous,
                "to": current,
                "change_pct": change_pct * 100,
                "type": change_type,
                "magnitude": "significant"
            })

    return significant_changes
```

### 2. 峰值/谷值检测

```python
def detect_peaks_and_valleys(values_series, window=3):
    """
    检测峰值和谷值
    values_series: 数值序列
    window: 检测窗口大小
    """
    peaks = []
    valleys = []

    n = len(values_series)

    for i in range(window, n - window):
        # 检查是否为峰值
        is_peak = True
        for j in range(1, window + 1):
            if values_series[i] <= values_series[i - j] or values_series[i] <= values_series[i + j]:
                is_peak = False
                break

        if is_peak:
            peaks.append({
                "position": i,
                "value": values_series[i],
                "type": "peak"
            })
            continue

        # 检查是否为谷值
        is_valley = True
        for j in range(1, window + 1):
            if values_series[i] >= values_series[i - j] or values_series[i] >= values_series[i + j]:
                is_valley = False
                break

        if is_valley:
            valleys.append({
                "position": i,
                "value": values_series[i],
                "type": "valley"
            })

    return peaks, valleys
```

### 3. 收益拐点检测

```python
def detect_profit_turning_points(market_value_slopes, shares_slopes, confidence=0.7):
    """
    检测收益拐点
    收益拐点：市值斜率与股数斜率的关系发生变化
    """
    turning_points = []

    for i in range(1, len(market_value_slopes)):
        prev_diff = market_value_slopes[i-1] - shares_slopes[i-1]
        curr_diff = market_value_slopes[i] - shares_slopes[i]

        # 检查收益类型是否发生变化
        prev_type = "positive" if prev_diff > 0 else "negative" if prev_diff < 0 else "neutral"
        curr_type = "positive" if curr_diff > 0 else "negative" if curr_diff < 0 else "neutral"

        if prev_type != curr_type:
            # 计算变化强度
            change_strength = abs(curr_diff - prev_diff)

            if change_strength >= confidence:
                turning_points.append({
                    "period": i,
                    "prev_type": prev_type,
                    "curr_type": curr_type,
                    "prev_diff": prev_diff,
                    "curr_diff": curr_diff,
                    "change_strength": change_strength
                })

    return turning_points
```

## 趋势检测算法

### 1. 移动平均趋势

```python
def calculate_moving_average_trend(values_series, window=3):
    """
    计算移动平均趋势
    """
    if len(values_series) < window:
        return "insufficient_data"

    # 计算移动平均
    moving_avg = []
    for i in range(len(values_series) - window + 1):
        avg = sum(values_series[i:i+window]) / window
        moving_avg.append(avg)

    # 分析移动平均趋势
    if len(moving_avg) < 2:
        return "unknown"

    first_half = moving_avg[:len(moving_avg)//2]
    second_half = moving_avg[len(moving_avg)//2:]

    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)

    if avg_second > avg_first * 1.1:
        return "strong_uptrend"
    elif avg_second > avg_first * 1.05:
        return "uptrend"
    elif avg_second < avg_first * 0.9:
        return "strong_downtrend"
    elif avg_second < avg_first * 0.95:
        return "downtrend"
    else:
        return "sideways"
```

### 2. Mann-Kendall趋势检验

```python
def mann_kendall_test(values_series):
    """
    Mann-Kendall趋势检验
    返回趋势方向和显著性
    """
    n = len(values_series)

    if n < 4:
        return {"trend": "insufficient_data", "p_value": 1.0}

    # 计算S统计量
    s = 0
    for i in range(n-1):
        for j in range(i+1, n):
            s += np.sign(values_series[j] - values_series[i])

    # 计算方差
    var_s = n * (n-1) * (2*n + 5) / 18

    # 计算Z值
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0

    # 计算p值（双尾检验）
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # 判断趋势
    if p_value < 0.05:
        if s > 0:
            trend = "significant_uptrend"
        else:
            trend = "significant_downtrend"
    else:
        trend = "no_significant_trend"

    return {
        "trend": trend,
        "s": s,
        "z": z,
        "p_value": p_value
    }
```

## 数据预处理

### 1. 缺失值处理

```python
def handle_missing_values(data_series, method="linear"):
    """
    处理缺失值
    method: 填充方法，可选 "linear", "forward", "backward", "zero"
    """
    if method == "linear":
        # 线性插值
        return pd.Series(data_series).interpolate(method='linear').tolist()
    elif method == "forward":
        # 前向填充
        return pd.Series(data_series).ffill().tolist()
    elif method == "backward":
        # 后向填充
        return pd.Series(data_series).bfill().tolist()
    elif method == "zero":
        # 填充0
        return [0 if pd.isna(x) else x for x in data_series]
    else:
        return data_series
```

### 2. 异常值检测和处理

```python
def detect_and_handle_outliers(data_series, threshold=2.0):
    """
    检测和处理异常值
    threshold: 标准差倍数阈值
    """
    data_array = np.array(data_series)
    mean = np.mean(data_array)
    std = np.std(data_array)

    # 检测异常值
    outliers = np.abs(data_array - mean) > threshold * std

    # 处理异常值（用中位数替换）
    if np.any(outliers):
        median = np.median(data_array)
        data_array[outliers] = median

    return data_array.tolist(), outliers.tolist()
```

## 权重计算

### 1. 时间序列加权

```python
def calculate_time_weights(n, method="linear"):
    """
    计算时间权重
    n: 时间点数量
    method: 权重计算方法
    """
    if method == "linear":
        # 线性递增权重
        return np.linspace(1, n, n)
    elif method == "exponential":
        # 指数权重（近期权重更高）
        return np.exp(np.linspace(0, 1, n))
    elif method == "equal":
        # 等权重
        return np.ones(n)
    else:
        return np.ones(n)
```

### 2. 数据标准化

```python
def standardize_data(data_series):
    """
    数据标准化（Z-score标准化）
    """
    data_array = np.array(data_series)
    mean = np.mean(data_array)
    std = np.std(data_array)

    if std == 0:
        return np.zeros_like(data_array).tolist()

    standardized = (data_array - mean) / std
    return standardized.tolist()
```

## 算法配置建议

### 默认配置

```python
DEFAULT_ALGORITHM_CONFIG = {
    # 斜率计算
    "slope_method": "linear_regression",
    "min_data_points": 4,

    # 精选算法
    "selection_weights": {
        "avg_weight": 0.3,
        "holding_stability": 0.25,
        "weight_trend": 0.2,
        "profit_performance": 0.15,
        "industry_representation": 0.1
    },

    # 操作节点
    "significant_change_threshold": 0.2,  # 20%
    "peak_detection_window": 3,

    # 趋势检测
    "trend_confidence_level": 0.95,

    # 异常值处理
    "outlier_threshold": 2.0,
    "handle_outliers": True
}
```

### 性能优化建议

1. **数据量小时**：使用简单斜率法，计算速度快
2. **数据量大时**：使用线性回归法，结果更稳定
3. **需要实时分析**：使用移动平均趋势检测，计算效率高
4. **需要统计显著性**：使用Mann-Kendall检验
5. **数据质量差**：增加异常值检测和缺失值处理

## 验证和测试

### 单元测试示例

```python
def test_slope_calculation():
    """测试斜率计算"""
    # 测试数据：明显的上升趋势
    y_values = [1, 2, 3, 4, 5]

    # 线性回归斜率应为1
    slope = calculate_slope_linear_regression(y_values)
    assert abs(slope - 1.0) < 0.001

    # 简单斜率也应约为1
    slope_simple = calculate_slope_simple(y_values)
    assert abs(slope_simple - 1.0) < 0.001
```

### 验证指标

1. **斜率计算的稳定性**：对噪声数据的鲁棒性
2. **精选算法的公平性**：不同特征的股票都能得到合理评分
3. **节点检测的准确性**：能准确识别重大变化点
4. **趋势判断的可靠性**：与实际趋势一致
5. **计算效率**：在大数据集上的性能表现