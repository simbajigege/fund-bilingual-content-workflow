# 基金持仓热力图数据分析技能

用于分析基金持仓热力图数据，提取关键投资信号，生成结构化报告和自然语言总结，支持投资博客内容生产工作流。

## 功能特点

- **数据获取**：通过基金代码自动调用API获取实时持仓数据
- **智能分析**：识别热力图关键信号（大/小色块+红/绿色组合）
- **多维分析**：财务指标、AI建议、行业分布全面分析
- **报告生成**：生成结构化JSON报告和自然语言分析总结
- **内容生产支持**：提供博客大纲、摘要报告等内容生产工具
- **可配置性**：支持阈值调整、权重配置等灵活设置

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 基本使用

1. **获取并分析基金数据**：

```bash
python scripts/fetch_and_analyze.py --fund-code 159730 --output-dir ./reports
```

2. **查看分析结果**：

```bash
# 查看自然语言总结
cat ./reports/*_summary.txt

# 查看博客大纲
cat ./reports/*_blog_outline.md
```

### 分步使用

1. **只获取数据**：

```bash
python scripts/fetch_data.py --fund-code 159730 --output data_159730.json
```

2. **只分析数据**：

```bash
python scripts/analyze_data.py --input data_159730.json --output analysis.json --summary-text summary.txt
```

## 输出文件说明

流水线运行后会在输出目录生成以下文件：

- `*_raw.json` - 原始API数据
- `*_analysis.json` - 结构化分析报告
- `*_summary.txt` - 自然语言分析总结
- `*_blog_outline.md` - 博客大纲（7段式）
- `*_brief.md` - 摘要报告
- `*_metadata.json` - 分析元数据

## 分析维度

### 1. 热力图信号分析
- 大色块+绿色：重仓且AI看好
- 大色块+红色：重仓但AI看空
- 小色块+绿色：轻仓但AI看好
- 整体颜色分析：持仓整体偏向

### 2. 财务指标分析
- 估值分析：PE/PB分位数
- 动量分析：涨幅/振幅
- 流动性分析：换手率/成交量

### 3. AI投资建议分析
- 操作建议分布统计
- 置信度与风险评估
- 目标价空间分析

### 4. 行业分布分析
- 行业集中度分析
- 细分龙头识别
- 赛道选择逻辑

## 内容生产工作流集成

### 博客写作流程

1. **数据获取** → 使用本技能获取分析结果
2. **选题策划** → 基于关键信号选择角度
3. **大纲生成** → 使用生成的博客大纲
4. **深度调研** → 针对重点股票深入研究
5. **内容写作** → 填充大纲，加入分析见解
6. **双语输出** → 生成中英文版本
7. **质量检查** → 使用检查清单

### 内容类型

1. **共识型文章**：重仓+AI看好的股票分析
2. **分歧型文章**：重仓但AI看空的争议分析
3. **潜力型文章**：轻仓但AI看好的潜力股分析
4. **风险型文章**：整体偏红的持仓风险警示

## API接口说明

### 数据接口

```
POST https://ai2alpha.cn/api/v1/stocks/ai-selected

请求体：
{
  "master_code": "基金代码",
  "limit": 200
}
```

### 返回字段

主要字段包括：
- `stock_code` - 股票代码
- `stock_name` - 股票名称
- `weight` - 持仓权重（%）
- `analysis_summary` - AI投资建议
  - `action` - 操作建议
  - `target_price` - 目标价格
  - `confidence` - 置信度
  - `risk_score` - 风险评分

## 配置说明

修改 `config.yaml` 文件调整分析参数：

```yaml
heatmap_thresholds:
  heavy_weight: 5.0    # 调整重仓阈值
  light_weight: 2.0    # 调整轻仓阈值

financial_thresholds:
  low_pe: 15.0         # 调整低PE阈值
  high_turnover: 3.0   # 调整高换手率阈值
```

## 使用示例

### 示例1：批量分析多个基金

```bash
#!/bin/bash
for fund_code in 159730 512880 515030; do
  python scripts/fetch_and_analyze.py --fund-code $fund_code --output-dir ./reports/$fund_code
done
```

### 示例2：集成到Python项目

```python
from scripts.analyze_data import FundHeatmapAnalyzer

analyzer = FundHeatmapAnalyzer()
data = {...}  # 加载数据
results = analyzer.analyze(data)
summary = analyzer.generate_summary(results)
```

### 示例3：生成内容生产材料

```bash
# 获取数据和分析
python scripts/fetch_and_analyze.py --fund-code 159730 --output-dir ./content_materials

# 使用生成的材料
# - blog_outline.md: 博客写作大纲
# - brief.md: 社交媒体摘要
# - summary.txt: 分析要点
```

## 高级功能

### 自定义分析逻辑

继承 `FundHeatmapAnalyzer` 类并重写分析方法：

```python
class CustomAnalyzer(FundHeatmapAnalyzer):
    def _analyze_heatmap_signals(self, stocks):
        # 自定义信号分析逻辑
        pass
```

### 集成到Web服务

```python
from flask import Flask, request, jsonify
from scripts.analyze_data import FundHeatmapAnalyzer

app = Flask(__name__)
analyzer = FundHeatmapAnalyzer()

@app.route('/analyze', methods=['POST'])
def analyze_fund():
    data = request.json
    results = analyzer.analyze(data)
    return jsonify(results)
```

## 故障排除

### 常见问题

1. **API请求失败**
   - 检查网络连接
   - 确认基金代码正确
   - 查看API服务状态

2. **数据验证失败**
   - 检查数据格式是否符合预期
   - 确认必需字段是否存在
   - 查看日志了解具体问题

3. **分析结果异常**
   - 检查配置阈值是否合理
   - 确认数据质量
   - 调整分析参数

### 日志查看

```bash
# 启用详细日志
python scripts/fetch_and_analyze.py --fund-code 159730 --verbose

# 查看日志文件
tail -f fund_analysis.log
```

## 更新日志

### v1.0.0 (2026-03-07)
- 初始版本发布
- 支持基金持仓数据获取与分析
- 生成结构化报告和自然语言总结
- 提供内容生产工作流支持

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

## 免责声明

本工具生成的分析结果仅供参考，不构成投资建议。投资有风险，决策需谨慎。