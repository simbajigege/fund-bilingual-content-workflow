# API数据字段说明

本文档详细说明基金持仓数据API返回的字段含义。

## 数据结构总览

API返回的JSON数据结构如下：

```json
{
  "master_code": "159730",
  "items": [
    {
      "id": 860,
      "master_code": "159730",
      "master_name": "博时国证龙头家电ETF",
      "master_description": "基金 159730(博时国证龙头家电ETF) 2025年4季度股票投资明细 的持仓数据",
      "a_positions": [...],
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

## 根级别字段

| 字段名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| `master_code` | string | 是 | 基金/大师代码 | "159730" |
| `items` | array | 是 | 季度持仓数据数组 | `[{...}, {...}]` |
| `total` | integer | 是 | 总数据条数（季度数） | 12 |

## 季度数据字段（items中的对象）

| 字段名 | 类型 | 必填 | 描述 | 示例 |
|--------|------|------|------|------|
| `id` | integer | 是 | 数据记录ID | 860 |
| `master_code` | string | 是 | 基金代码 | "159730" |
| `master_name` | string | 是 | 基金名称 | "博时国证龙头家电ETF" |
| `master_description` | string | 是 | 数据描述 | "基金 159730(博时国证龙头家电ETF) 2025年4季度股票投资明细 的持仓数据" |
| `a_positions` | array | 是 | A股持仓明细数组 | `[{...}, {...}]` |
| `hk_positions` | array | 是 | 港股持仓明细数组 | `[]` |
| `us_positions` | array | 是 | 美股持仓明细数组 | `[]` |
| `as_of_date` | string | 是 | 数据截止日期（YYYY-MM-DD格式） | "2025-12-01" |
| `created_at` | string | 是 | 数据创建时间 | "2026-03-02T18:58:17.290150" |
| `updated_at` | string | 是 | 数据更新时间 | "2026-03-02T18:58:17.290150" |

## 持仓明细字段（a_positions中的对象）

| 字段名 | 类型 | 必填 | 描述 | 示例 | 计算公式 |
|--------|------|------|------|------|----------|
| `stock_code` | string | 是 | 股票代码 | "002050" | - |
| `stock_name` | string | 是 | 股票名称 | "三花智控" | - |
| `shares` | number | 是 | 持仓股数 | 93800.0 | - |
| `market_value` | number | 是 | 持仓市值（元） | 5188099.999999999 | - |
| `weight` | number | 是 | 持仓权重（百分比） | 14.78 | `(market_value / 基金总市值) × 100` |

## 日期格式说明

### `as_of_date` 字段
- 格式：YYYY-MM-DD
- 示例："2025-12-01"
- 说明：表示该季度持仓数据的截止日期，通常是季度末的最后一天

### `created_at` 和 `updated_at` 字段
- 格式：ISO 8601，包含时区信息
- 示例："2026-03-02T18:58:17.290150"
- 说明：数据在服务器上的创建和更新时间

## 数据单位说明

| 字段 | 单位 | 转换说明 |
|------|------|----------|
| `shares` | 股 | 1股 = 1股 |
| `market_value` | 元（人民币） | 1元 = 1元 |
| `weight` | 百分比（%） | 例如：14.78 表示 14.78% |

## 多市场支持

目前API支持三个市场的持仓数据：
1. **A股** (`a_positions`): 中国大陆A股市场
2. **港股** (`hk_positions`): 香港股票市场
3. **美股** (`us_positions`): 美国股票市场

在当前的示例数据中，`hk_positions` 和 `us_positions` 为空数组，表示该基金只持有A股。

## 数据质量注意事项

1. **精度问题**: `shares` 和 `market_value` 字段可能存在浮点数精度问题（如 93800.00000000001）
2. **缺失值**: 理论上所有字段都应存在，但实际数据中可能出现空值
3. **数据一致性**: `weight` 字段之和应接近100%，但可能存在轻微偏差
4. **时间顺序**: `items` 数组中的季度数据应按时间倒序排列（最近的季度在前）

## 数据验证规则

1. `stock_code` 应为6位数字代码（A股）
2. `shares` 应大于0
3. `market_value` 应大于0
4. `weight` 应在0-100之间
5. `as_of_date` 应为有效的日期格式
6. 同一季度内，同一 `stock_code` 不应重复出现

## 常用数据转换

### 转换为双轴图CSV格式

双轴图CSV需要以下字段：
- `quarter`: 季度（从 `as_of_date` 转换而来，格式如 "2025Q4"）
- `ticker`: 股票代码
- `market_value_100m`: 持仓市值（以100M为单位，即1亿）
- `shares_million`: 持仓股数（以百万股为单位）

转换公式：
```python
market_value_100m = market_value / 100000000  # 1亿 = 100,000,000元
shares_million = shares / 1000000              # 1百万股 = 1,000,000股
quarter = f"{as_of_date[:4]}Q{(int(as_of_date[5:7]) + 2) // 3}"  # 月份转季度
```

### 季度转换规则

月份到季度的转换：
- 1-3月: Q1
- 4-6月: Q2
- 7-9月: Q3
- 10-12月: Q4

## 示例数据片段

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