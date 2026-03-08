# 基金个股持仓双轴历史图分析技能

一个用于分析基金历史持仓数据，生成个股持仓市值与股数双轴历史图数据的专业技能。

## 功能概述

本技能基于基金多季度持仓数据，通过智能算法：
1. **精选关键个股**：基于权重、稳定性、收益表现等多维度评分
2. **生成双轴图数据**：输出标准CSV格式，可直接用于可视化
3. **分析收益表现**：识别大师在个股上的正/负收益表现
4. **识别操作节点**：发现大幅加仓/减仓时机和收益拐点
5. **生成分析报告**：提供结构化JSON报告和自然语言总结

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 一站式分析（推荐）
```bash
python scripts/fetch_and_analyze.py --fund-code 159730 --report-dir ./reports --csv-dir ./csv_data
```

### 分步骤分析
```bash
# 1. 获取数据
python scripts/fetch_historical_data.py --fund-code 159730 --quarters 12 --output data.json

# 2. 分析数据
python scripts/analyze_dual_axis.py --input data.json --output analysis.json --csv-dir ./csv_data
```

## 输出示例

### 双轴图CSV数据
```csv
quarter,ticker,market_value_100m,shares_million
2025Q3,002050,5.54,114.3
2025Q4,002050,5.19,93.8
```

### 分析报告（JSON）
包含完整的分析结果，包括：
- 关键个股精选结果和评分
- 斜率分析和收益类型判断
- 操作节点识别
- 行业分布分析
- 博客内容生产建议

### 自然语言总结
生成易于理解的中文分析总结，可直接用于内容生产。

## 配置说明

详细配置请参考 [config.yaml](config.yaml)，主要配置项包括：

- **个股精选阈值**：权重、稳定性、趋势等筛选条件
- **双轴图分析参数**：市值和股数单位、显著变化阈值
- **收益分析标准**：正收益、高收益、亏损等阈值
- **输出格式设置**：JSON缩进、CSV编码、语言等

## 内容生产工作流集成

本技能的输出可直接用于投资博客内容生产工作流：

1. **双轴图可视化**：使用生成的CSV数据创建图表
2. **选题矩阵生成**：基于收益分析和操作节点生成选题
3. **深度调研指导**：为重点个股提供历史数据支持
4. **博客结构设计**：提供7段式博客结构的数据依据

## 文件结构

```
fund-dual-axis-analysis/
├── SKILL.md                    # 技能详细说明
├── config.yaml                 # 配置文件
├── requirements.txt            # Python依赖
├── scripts/                    # Python脚本
│   ├── fetch_historical_data.py
│   ├── analyze_dual_axis.py
│   ├── fetch_and_analyze.py
│   └── analyzer.py
├── references/                 # 参考文档
│   ├── data_fields.md
│   ├── analysis_algorithms.md
│   ├── output_templates.md
│   └── content_production.md
├── assets/                     # 示例数据
│   ├── example_data.json
│   └── example_dual_axis.csv
└── README.md                   # 本文件
```

## 使用场景

### 投资研究
- 分析大师持仓变化和收益表现
- 识别关键操作节点和投资逻辑
- 评估行业分布和龙头偏好

### 内容生产
- 生成数据驱动的投资分析文章
- 创建可视化图表和解读内容
- 构建系统化的投资分析框架

### 教育学习
- 学习大师投资策略和择时方法
- 理解持仓数据分析方法
- 掌握投资分析工具开发

## 扩展开发

### 自定义分析算法
通过修改 `scripts/analyzer.py` 中的算法实现自定义分析逻辑。

### 集成其他数据源
通过扩展 `scripts/fetch_historical_data.py` 支持更多数据源。

### 自定义输出格式
通过修改 `references/output_templates.md` 中的模板调整输出格式。

## 注意事项

1. **数据质量**：分析结果依赖数据质量和完整性
2. **时间跨度**：建议至少4个季度数据以获得可靠趋势
3. **行业分类**：当前版本使用简化行业分类，可根据需要扩展
4. **风险提示**：历史表现不代表未来，投资需谨慎

## 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 支持

如有问题或建议，请提交Issue或联系维护者。