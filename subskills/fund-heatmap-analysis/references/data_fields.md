# 数据字段说明

本文档详细说明API返回的基金持仓数据字段含义。

## 数据结构概览

API返回的JSON数据结构如下：

```json
{
  "success": boolean,
  "data": [
    {
      // 个股持仓数据
    }
  ],
  "meta": {
    // 元数据
  }
}
```

## 个股持仓字段说明

### 基础信息字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `stock_code` | string | 股票代码 | "002508" |
| `stock_name` | string | 股票名称 | "老板电器" |
| `current_price` | float | 当前价格 | 20.44 |
| `change_pct` | float | 涨跌幅百分比 | 2.149 |
| `change_amount` | float | 涨跌额 | 0.43 |
| `volume` | integer | 成交量（股） | 6297316 |
| `amount` | integer | 成交额（元） | 127905153 |
| `amplitude` | float | 振幅百分比 | 3.998 |
| `high_price` | float | 最高价 | 20.65 |
| `low_price` | float | 最低价 | 19.85 |
| `open_price` | float | 开盘价 | 19.9 |
| `pre_close` | float | 前收盘价 | 20.01 |
| `turnover_rate` | float | 换手率百分比 | 0.6746 |
| `pe_ratio` | float | 市盈率 | 12.24 |
| `pb_ratio` | float | 市净率 | 1.692 |
| `total_market_cap` | float | 总市值 | 19314551443.04 |
| `circulating_market_cap` | float | 流通市值 | 19081798526.28 |
| `industry` | string | 行业分类 | "家电行业" |
| `org_name_cn` | string | 公司中文名 | "杭州老板电器股份有限公司" |
| `org_name_en` | string | 公司英文名 | "Hangzhou Robam Appliances Co.,Ltd." |
| `org_short_name_en` | string | 公司英文简称 | "ROBAM" |
| `stock_type` | string | 股票类型 | "A" |
| `collection_time` | string | 数据收集时间 | "2026-03-06T15:14:06.323010" |

### 持仓相关字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `shares` | integer | 持仓股数 | 47000 |
| `weight` | float | 持仓权重百分比 | 2.59 |
| `market_value` | integer | 持仓市值 | 909100 |

### AI投资建议字段

`analysis_summary` 对象包含AI投资建议：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `action` | string | 操作建议 | "持有" |
| `target_price` | float | 目标价格 | 23 |
| `confidence` | float | 置信度（0-1） | 0.6 |
| `risk_score` | float | 风险评分（0-1） | 0.6 |
| `reasoning` | string | 推理过程 | "地产政策传导存在滞后性..." |
| `buy_price` | float | 建议买入价 | 20.44 |
| `sell_price` | float | 建议卖出价 | 19 |

### AI评级映射规则

根据`analysis_summary.action`字段映射到标准AI评级：

| action值 | AI评级 | 颜色 |
|----------|--------|------|
| "强力买入" | "Strong Buy" | 深绿 |
| "买入" | "Buy" | 浅绿 |
| "持有" | "Hold" | 黄色 |
| "卖出" | "Sell" | 浅红 |
| "强力卖出" | "Strong Sell" | 深红 |

## 元数据字段说明

`meta` 对象包含查询元数据：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `total_selected_codes` | integer | 选股总数 | 10 |
| `total_count` | integer | 返回总数 | 10 |
| `analysis_report_total_count` | integer | 分析报告总数 | 18968 |
| `latest_trade_date_report_count` | integer | 最新交易日报告数 | 363 |
| `limit` | integer | 查询限制 | 200 |
| `sort_by` | string | 排序字段 | "change_pct" |
| `sort_order` | string | 排序顺序 | "desc" |
| `from_cache` | boolean | 是否来自缓存 | true |
| `master_code` | string | 基金代码 | "159730" |

## 计算字段说明

### 持仓权重百分比（portfolio_weight_pct）

从`weight`字段直接获取，表示该股票在基金总持仓中的权重百分比。

### AI评分（ai_score）

根据以下规则计算AI评分（0-100）：
1. `action`映射为基础分：Strong Buy=90, Buy=75, Hold=50, Sell=25, Strong Sell=10
2. 根据`confidence`调整：基础分 × `confidence`
3. 根据`risk_score`调整：结果 × (1 - `risk_score`/2)

公式：`ai_score = base_score * confidence * (1 - risk_score/2)`

## 数据质量说明

1. **数据来源**：API从ai2alpha.cn获取
2. **更新频率**：交易日实时更新
3. **数据完整性**：包含A股主要财务指标和AI分析
4. **时间戳**：`collection_time`为ISO 8601格式

## 使用注意事项

1. **权重计算**：`weight`字段为百分比，需除以100得到小数形式
2. **价格单位**：所有价格单位为人民币元
3. **市值单位**：市值为人民币元，注意数值较大
4. **时间处理**：`collection_time`为UTC时间，需转换为本地时间
5. **空值处理**：部分字段可能为空，需进行空值检查