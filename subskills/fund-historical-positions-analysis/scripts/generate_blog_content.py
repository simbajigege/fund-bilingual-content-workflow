#!/usr/bin/env python3
"""
博客内容框架生成脚本

基于基金历史持仓权重分析结果，生成博客内容框架
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BlogContentGenerator:
    """博客内容生成器"""

    def __init__(self):
        """初始化生成器"""
        self.templates = {
            "7segment": self._generate_7segment_blog,
            "simple": self._generate_simple_blog,
            "detailed": self._generate_detailed_blog
        }

    def load_analysis_report(self, filepath: str) -> Dict[str, Any]:
        """
        加载分析报告

        Args:
            filepath: 分析报告文件路径

        Returns:
            分析报告数据
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"从 {filepath} 加载分析报告")
            return data

        except FileNotFoundError:
            logger.error(f"文件不存在: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise

    def generate_blog_content(self, analysis_report: Dict[str, Any],
                            template_type: str = "7segment") -> str:
        """
        生成博客内容

        Args:
            analysis_report: 分析报告
            template_type: 模板类型

        Returns:
            博客内容
        """
        if template_type not in self.templates:
            logger.warning(f"模板类型 {template_type} 不存在，使用7segment模板")
            template_type = "7segment"

        generator_func = self.templates[template_type]
        return generator_func(analysis_report)

    def _generate_7segment_blog(self, analysis_report: Dict[str, Any]) -> str:
        """
        生成7段式博客内容

        Args:
            analysis_report: 分析报告

        Returns:
            7段式博客内容
        """
        metadata = analysis_report.get("metadata", {})
        stability = analysis_report.get("stability_analysis", {})
        trend = analysis_report.get("trend_analysis", {})
        style = analysis_report.get("style_assessment", {})
        key_signals = analysis_report.get("key_signals", [])
        recommendations = analysis_report.get("recommendations", {})

        fund_code = metadata.get("fund_code", "unknown")
        fund_name = metadata.get("fund_name", "unknown")
        quarters = metadata.get("quarters_analyzed", [])
        unique_stocks = metadata.get("unique_stocks", 0)

        overall_stability = stability.get("overall_stability_score", 0)
        style_type = style.get("type", "unknown")
        style_interpretation = style.get("interpretation", "")
        turnover_rate = style.get("turnover_rate", 0)

        # 获取关键股票信息
        high_stability = stability.get("high_stability_stocks", [])
        increasing = trend.get("increasing_trend_stocks", [])
        decreasing = trend.get("decreasing_trend_stocks", [])

        # 确定标题角度
        title_angle = self._determine_title_angle(analysis_report)

        # 构建7段式博客
        blog_content = f"""# {fund_code}持仓分析：{title_angle}的投资启示

## 1. 开篇：历史持仓堆叠图全景一览
[工具截图 Placeholder - 历史持仓权重堆叠图 · {fund_name} · 近{len(quarters)}季度]

说明：
- 横轴：时间（季度），从{quarters[-1]}到{quarters[0]}
- 纵轴：各股票持仓权重百分比
- 色块含义：不同颜色代表不同股票，色块高度代表权重
- 关键观察点：
"""

        # 添加关键观察点
        if high_stability:
            stock = high_stability[0]
            blog_content += f"  1. {stock.get('stock_name', stock.get('stock_code'))}（{stock.get('stock_code')}）色块长期稳定在{stock.get('min_weight', 0):.1f}-{stock.get('max_weight', 0):.1f}%区间\n"

        if increasing:
            stock = increasing[0]
            blog_content += f"  2. {stock.get('stock_name', stock.get('stock_code'))}（{stock.get('stock_code')}）色块逐渐升高，显示加仓趋势\n"

        if decreasing:
            stock = decreasing[0]
            blog_content += f"  3. {stock.get('stock_name', stock.get('stock_code'))}（{stock.get('stock_code')}）色块逐渐降低，显示减仓趋势\n"

        blog_content += f"""
读者引导：点击图片可跳转工具页面，查看实时堆叠图数据

## 2. 稳定性分析："抄作业"首选清单
基于{len(quarters)}个季度数据分析，该基金持仓整体稳定性评分为 **{overall_stability}/100**。

**高稳定性核心持仓（稳定性>85分）：**
"""

        # 添加核心持仓
        for i, stock in enumerate(high_stability[:3]):
            blog_content += f"{i+1}. **{stock.get('stock_name', stock.get('stock_code'))}（{stock.get('stock_code')}）**\n"
            blog_content += f"   - 稳定性：{stock.get('stability_score')}分\n"
            blog_content += f"   - 平均权重：{stock.get('avg_weight')}%\n"
            blog_content += f"   - 权重范围：{stock.get('min_weight')}%-{stock.get('max_weight')}%\n"
            blog_content += f"   - 连续持仓：{len(quarters)}个季度\n"

        blog_content += f"""
**投资启示：**
对于普通投资者，这些高稳定性核心持仓适合直接"抄作业"。基金经理长期重仓这些股票，说明其投资逻辑清晰且一致，普通投资者跟踪难度低。

## 3. 变动趋势：基金经理的调仓信号
### 持续加仓信号
"""

        if increasing:
            for i, stock in enumerate(increasing[:2]):
                blog_content += f"{i+1}. **{stock.get('stock_name', stock.get('stock_code'))}（{stock.get('stock_code')}）**\n"
                blog_content += f"   - 当前权重：{stock.get('current_weight')}%\n"
                blog_content += f"   - 变化幅度：{stock.get('weight_change')}%\n"
                blog_content += f"   - 趋势强度：{stock.get('trend_strength')}\n"
                blog_content += f"   - 信号解读：基金经理持续看好，可能基于[逻辑分析]\n"
        else:
            blog_content += "暂无显著持续加仓信号\n"

        blog_content += f"""
### 持续减仓信号
"""

        if decreasing:
            for i, stock in enumerate(decreasing[:2]):
                blog_content += f"{i+1}. **{stock.get('stock_name', stock.get('stock_code'))}（{stock.get('stock_code')}）**\n"
                blog_content += f"   - 当前权重：{stock.get('current_weight')}%\n"
                blog_content += f"   - 变化幅度：{stock.get('weight_change')}%\n"
                blog_content += f"   - 趋势强度：{stock.get('trend_strength')}\n"
                blog_content += f"   - 信号解读：基金经理逐步减仓，需关注[风险因素]\n"
        else:
            blog_content += "暂无显著持续减仓信号\n"

        blog_content += f"""
**趋势解读：**
加仓股票反映基金经理当前看好方向，减仓股票提示潜在风险。普通投资者应重点关注加仓趋势，同时谨慎对待减仓信号。

## 4. 风格评估：这是什么样的基金经理？
**风格类型：{style_type}**
- 季度换手率：{turnover_rate:.1f}%
- 整体稳定性：{overall_stability}/100
- 风格特征：{style_interpretation}

**适合跟踪程度：{style.get('suitability', 'unknown').upper()}**
- 跟踪难度：{style.get('tracking_difficulty', 'unknown')}
- 适合投资者：{self._get_suitable_investors(style_type)}

**13F数据滞后影响评估：**
基金持仓数据存在45天披露延迟。对于{style_type}风格：
- 滞后影响：{self._get_lag_impact(style_type, turnover_rate)}
- 跟踪建议：{self._get_tracking_suggestion(style_type)}

## 5. 关键股票深度分析
### 重点股票1：稳定性之王
"""

        if high_stability:
            stock = high_stability[0]
            blog_content += f"""**{stock.get('stock_name', stock.get('stock_code'))}（{stock.get('stock_code')}）**

**持仓特征：**
- 连续{len(quarters)}个季度持仓，从未缺席
- 稳定性评分：{stock.get('stability_score')}分（满分100）
- 平均权重：{stock.get('avg_weight')}%，波动仅±{stock.get('weight_std')}%
- 持仓排名：稳定在前3名内

**投资逻辑分析：**
基金经理长期重仓该股票，可能基于以下考虑：
1. [行业龙头地位]
2. [稳定的现金流和分红]
3. [明确的增长前景]
4. [良好的估值水平]

**适合投资者类型：**
- 保守型投资者：作为"压舱石"配置
- 长期投资者：关注长期价值
- 新手投资者："抄作业"首选
"""

        blog_content += f"""
### 重点股票2：加仓明星
"""

        if increasing:
            stock = increasing[0]
            blog_content += f"""**{stock.get('stock_name', stock.get('stock_code'))}（{stock.get('stock_code')}）**

**持仓特征：**
- 当前权重：{stock.get('current_weight')}%
- 变化趋势：连续{len(quarters)-1}个季度加仓
- 总变化幅度：{stock.get('weight_change')}%
- 趋势斜率：{stock.get('slope')}（每季度）

**加仓逻辑推测：**
基金经理持续加仓，可能反映：
1. [基本面改善预期]
2. [估值修复机会]
3. [行业景气度提升]
4. [公司独特竞争优势]

**风险提示：**
1. 加仓后可能面临调整风险
2. 需关注公司最新财报和公告
3. 注意行业政策变化影响
"""

        blog_content += f"""
## 6. 风险评估与局限性
### 数据滞后风险
13F持仓数据延迟45天披露，对于{style_type}风格基金：
- 实际影响：{self._get_lag_impact_detail(style_type, turnover_rate)}
- 应对策略：{self._get_lag_mitigation(style_type)}

### 行业集中风险
"""

        # 添加行业分析（如果有）
        concentration_ratio = style.get("concentration_ratio", 0)
        if concentration_ratio > 60:
            blog_content += f"持仓高度集中（前5大持仓占比{concentration_ratio:.1f}%），行业波动可能对基金业绩产生较大影响。\n"
        elif concentration_ratio > 40:
            blog_content += f"持仓适度集中（前5大持仓占比{concentration_ratio:.1f}%），需关注主要持仓行业的景气度变化。\n"
        else:
            blog_content += "持仓相对分散，行业风险相对可控。\n"

        blog_content += f"""
### 波动性风险
"""

        high_volatility = stability.get("high_volatility_stocks", [])
        if high_volatility:
            blog_content += f"部分股票持仓波动较大（如{high_volatility[0].get('stock_name', high_volatility[0].get('stock_code'))}），普通投资者跟踪困难。\n"
        else:
            blog_content += "整体持仓波动性较低，跟踪难度适中。\n"

        blog_content += f"""
### 方法论局限性
1. 分析基于历史数据，不代表未来表现
2. 权重计算可能存在四舍五入误差
3. 季度数据粒度较粗，可能错过月度变化
4. 仅分析A股持仓，未包含港股/美股

## 7. 投资建议与行动指南
### 适合的投资者画像
{self._get_investor_profile(style_type, overall_stability)}

### 具体操作建议
1. **核心配置**：重点配置高稳定性核心持仓
2. **趋势跟随**：适度关注加仓趋势股票
3. **风险控制**：避开高波动性持仓，除非有深入研究
4. **仓位管理**：根据个人风险承受能力确定仓位比例

### 后续跟踪要点
1. **时间节点**：季度财报发布后关注持仓变化
2. **关键指标**：核心持仓的财务表现和估值变化
3. **风险监控**：关注行业政策变化和宏观风险
4. **风格验证**：持续观察基金经理风格是否一致

### 行动清单
- [ ] 研究核心持仓的基本面和估值
- [ ] 分析加仓趋势股票的投资逻辑
- [ ] 评估个人风险承受能力与基金风格的匹配度
- [ ] 制定具体的买入/持有/卖出计划
- [ ] 设置定期回顾和调整机制

---

## 附录：数据与方法说明
### 数据来源
- 基金持仓数据：ai2alpha.cn基金多季度持仓数据
- 分析期间：{quarters[-1]} 至 {quarters[0]}（共{len(quarters)}个季度）
- 分析股票：{unique_stocks}只A股持仓

### 关键指标说明
1. **稳定性评分**：基于权重标准差、变动率、连续性综合计算（0-100分）
2. **趋势斜率**：权重时间序列的线性回归斜率，反映变化速度
3. **季度换手率**：相邻季度持仓股票变动的平均比例
4. **集中度**：前5大持仓权重占比

### 免责声明
本文为基于公开数据的分析报告，不构成任何投资建议。投资有风险，入市需谨慎。读者应基于独立判断做出投资决策，并对自己的投资行为负责。

---
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*分析方法：历史持仓权重堆叠图分析*
*分析工具：fund-historical-positions-analysis技能*
"""

        return blog_content

    def _generate_simple_blog(self, analysis_report: Dict[str, Any]) -> str:
        """
        生成简版博客内容

        Args:
            analysis_report: 分析报告

        Returns:
            简版博客内容
        """
        metadata = analysis_report.get("metadata", {})
        stability = analysis_report.get("stability_analysis", {})
        key_signals = analysis_report.get("key_signals", [])

        fund_code = metadata.get("fund_code", "unknown")
        fund_name = metadata.get("fund_name", "unknown")
        overall_stability = stability.get("overall_stability_score", 0)

        # 获取前3个关键信号
        top_signals = key_signals[:3]

        blog_content = f"""# 快速解读：{fund_code}基金持仓的{len(top_signals)}个关键信号

## 信号概览
整体稳定性：{overall_stability}/100（{'高度稳定' if overall_stability >= 80 else '适度稳定' if overall_stability >= 60 else '波动较大'}）

"""

        for i, signal in enumerate(top_signals):
            stock_name = signal.get("stock_name", signal.get("stock_code"))
            desc = signal.get("description", "")
            priority = signal.get("priority", "")

            blog_content += f"## 信号{i+1}：{stock_name}（{priority}）\n"
            blog_content += f"{desc}\n\n"

            # 根据信号类型添加内容
            signal_type = signal.get("signal_type", "")
            if "core_holding" in signal_type:
                blog_content += "**投资启示：**\n"
                blog_content += "- 适合作为核心持仓配置\n"
                blog_content += "- 稳定性高，跟踪难度低\n"
                blog_content += "- 普通投资者可直接\"抄作业\"\n\n"
            elif "increasing" in signal_type:
                blog_content += "**投资启示：**\n"
                blog_content += "- 显示基金经理看好\n"
                blog_content += "- 可适度跟随加仓趋势\n"
                blog_content += "- 需关注加仓逻辑和风险\n\n"
            elif "volatility" in signal_type:
                blog_content += "**投资启示：**\n"
                blog_content += "- 波动较大，跟踪需谨慎\n"
                blog_content += "- 适合风险承受能力高的投资者\n"
                blog_content += "- 需要更深入的研究\n\n"

        blog_content += f"""
## 快速建议
1. **重点关注**：{', '.join([s.get('stock_name', s.get('stock_code')) for s in top_signals if 'core' in s.get('signal_type', '')][:2])}
2. **适度关注**：{', '.join([s.get('stock_name', s.get('stock_code')) for s in top_signals if 'increasing' in s.get('signal_type', '')][:1])}
3. **谨慎对待**：{', '.join([s.get('stock_name', s.get('stock_code')) for s in top_signals if 'volatility' in s.get('signal_type', '')][:1])}

## 风险提示
- 数据滞后45天，注意时效性
- 本文为数据分析，不构成投资建议
- 投资需根据个人风险承受能力决策

---
*分析时间：{datetime.now().strftime('%Y-%m-%d')}*
*数据来源：ai2alpha.cn*
"""

        return blog_content

    def _generate_detailed_blog(self, analysis_report: Dict[str, Any]) -> str:
        """
        生成详细版博客内容

        Args:
            analysis_report: 分析报告

        Returns:
            详细版博客内容
        """
        # 使用7段式模板作为基础，但更详细
        base_content = self._generate_7segment_blog(analysis_report)

        # 在详细版中添加更多分析
        stability = analysis_report.get("stability_analysis", {})
        trend = analysis_report.get("trend_analysis", {})
        style = analysis_report.get("style_assessment", {})

        high_stability = stability.get("high_stability_stocks", [])
        high_volatility = stability.get("high_volatility_stocks", [])
        increasing = trend.get("increasing_trend_stocks", [])
        decreasing = trend.get("decreasing_trend_stocks", [])
        concentration_ratio = style.get("concentration_ratio", 0)

        # 在适当位置插入详细分析
        detailed_sections = []

        # 添加详细稳定性分析
        if high_stability:
            detailed_sections.append("""
### 稳定性分析详细指标
| 股票 | 稳定性评分 | 权重标准差 | 变动率 | 连续性 |
|------|------------|------------|--------|--------|
""")
            for stock in high_stability[:5]:
                detailed_sections.append(f"| {stock.get('stock_name', stock.get('stock_code'))} | {stock.get('stability_score')} | {stock.get('weight_std')} | {(stock.get('max_weight', 0)-stock.get('min_weight', 0))/stock.get('avg_weight', 1)*100:.1f}% | 100% |\n")

        # 添加详细趋势分析
        if increasing or decreasing:
            detailed_sections.append("""
### 趋势分析详细数据
| 趋势类型 | 股票 | 当前权重 | 总变化 | 季度斜率 | 趋势强度 |
|----------|------|----------|--------|----------|----------|
""")
            for stock in increasing[:3]:
                detailed_sections.append(f"| 加仓 | {stock.get('stock_name', stock.get('stock_code'))} | {stock.get('current_weight')}% | {stock.get('weight_change')}% | {stock.get('slope')} | {stock.get('trend_strength')} |\n")

            for stock in decreasing[:3]:
                detailed_sections.append(f"| 减仓 | {stock.get('stock_name', stock.get('stock_code'))} | {stock.get('current_weight')}% | {stock.get('weight_change')}% | {stock.get('slope')} | {stock.get('trend_strength')} |\n")

        # 添加集中度分析
        detailed_sections.append(f"""
### 持仓集中度分析
- 前5大持仓集中度：{concentration_ratio:.1f}%
- Herfindahl指数：{concentration_ratio/100:.3f}
- 集中度解读：{"高度集中" if concentration_ratio > 60 else "适度集中" if concentration_ratio > 40 else "相对分散"}
""")

        # 添加波动性分析
        if high_volatility:
            detailed_sections.append("""
### 高波动性股票详细分析
| 股票 | 稳定性评分 | 平均权重 | 权重标准差 | 波动原因 |
|------|------------|----------|------------|----------|
""")
            for stock in high_volatility:
                detailed_sections.append(f"| {stock.get('stock_name', stock.get('stock_code'))} | {stock.get('stability_score')} | {stock.get('avg_weight')}% | {stock.get('weight_std')} | {stock.get('volatility_reason', '权重季度间调整频繁')} |\n")

        # 将详细部分插入到博客中（在第5部分后）
        parts = base_content.split("## 5. 关键股票深度分析")
        if len(parts) > 1:
            detailed_content = parts[0] + "## 5. 关键股票深度分析" + "\n".join(detailed_sections) + parts[1]
            return detailed_content
        else:
            return base_content

    def _determine_title_angle(self, analysis_report: Dict[str, Any]) -> str:
        """确定标题角度"""
        stability = analysis_report.get("stability_analysis", {})
        trend = analysis_report.get("trend_analysis", {})
        style = analysis_report.get("style_assessment", {})

        overall_stability = stability.get("overall_stability_score", 0)
        style_type = style.get("type", "")

        increasing = trend.get("increasing_trend_stocks", [])
        decreasing = trend.get("decreasing_trend_stocks", [])

        if overall_stability >= 85:
            return "稳定持仓的" + ("加仓信号" if increasing else "投资启示")
        elif increasing and decreasing:
            return "共识与分歧"
        elif increasing:
            return "加仓趋势"
        elif decreasing:
            return "减仓警示"
        elif style_type == "active_trading":
            return "频繁调仓"
        else:
            return "持仓分析"

    def _get_suitable_investors(self, style_type: str) -> str:
        """获取适合的投资者类型"""
        if style_type == "conservative_stable":
            return "保守型投资者、长期投资者、新手投资者"
        elif style_type == "moderate_adjustment":
            return "平衡型投资者、有一定分析能力的投资者"
        else:  # active_trading
            return "激进型投资者、专业投资者、有深度研究能力的投资者"

    def _get_lag_impact(self, style_type: str, turnover_rate: float) -> str:
        """获取数据滞后影响"""
        if style_type == "conservative_stable" or turnover_rate < 15:
            return "极小，持仓稳定"
        elif turnover_rate < 30:
            return "有限，适度调整"
        else:
            return "较大，频繁调仓"

    def _get_tracking_suggestion(self, style_type: str) -> str:
        """获取跟踪建议"""
        if style_type == "conservative_stable":
            return "可直接跟踪，滞后影响小"
        elif style_type == "moderate_adjustment":
            return "可跟踪但需注意数据滞后"
        else:
            return "跟踪难度大，建议谨慎"

    def _get_lag_impact_detail(self, style_type: str, turnover_rate: float) -> str:
        """获取数据滞后影响详情"""
        if style_type == "conservative_stable" or turnover_rate < 15:
            return "持仓结构长期稳定，45天延迟对投资信号影响极小"
        elif turnover_rate < 30:
            return "持仓适度调整，45天延迟可能错过部分调仓信号，但核心持仓不变"
        else:
            return "持仓频繁变动，45天延迟可能导致信号失效，跟踪价值降低"

    def _get_lag_mitigation(self, style_type: str) -> str:
        """获取滞后缓解策略"""
        if style_type == "conservative_stable":
            return "关注核心持仓的长期逻辑，忽略短期波动"
        elif style_type == "moderate_adjustment":
            return "结合最新季报和行业新闻，验证持仓变化的持续性"
        else:
            return "谨慎参考历史持仓，更多依赖实时基本面和市场分析"

    def _get_investor_profile(self, style_type: str, stability_score: float) -> str:
        """获取投资者画像"""
        if style_type == "conservative_stable":
            return f"""
1. **风险偏好**：低风险
2. **投资经验**：新手到中级
3. **时间投入**：有限，希望"抄作业"
4. **收益预期**：稳健增长，跑赢通胀
5. **适合理由**：持仓稳定({stability_score}/100)，跟踪难度低
"""
        elif style_type == "moderate_adjustment":
            return f"""
1. **风险偏好**：中等风险
2. **投资经验**：中级，有一定分析能力
3. **时间投入**：适度，愿意花时间研究
4. **收益预期**：中等增长，适度波动
5. **适合理由**：适度调整，既有稳定性又有灵活性
"""
        else:
            return f"""
1. **风险偏好**：高风险
2. **投资经验**：高级，有深度研究能力
3. **时间投入**：大量，密切关注市场
4. **收益预期**：高增长，接受较大波动
5. **适合理由**：风格激进，可能捕捉超额收益但风险也高
"""

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生成博客内容框架')
    parser.add_argument('--report', '-r', required=True, help='分析报告文件路径')
    parser.add_argument('--output', '-o', help='博客内容输出路径')
    parser.add_argument('--template', '-t', default='7segment',
                       choices=['7segment', 'simple', 'detailed'],
                       help='模板类型（默认：7segment）')
    parser.add_argument('--verbose', '-v', action='store_true', help='输出详细信息')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # 初始化生成器
        generator = BlogContentGenerator()

        # 加载分析报告
        logger.info(f"加载分析报告: {args.report}")
        analysis_report = generator.load_analysis_report(args.report)

        # 生成博客内容
        logger.info(f"生成博客内容，使用{args.template}模板...")
        blog_content = generator.generate_blog_content(analysis_report, args.template)

        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(blog_content)
            logger.info(f"博客内容已保存: {args.output}")

            # 输出统计信息
            word_count = len(blog_content.split())
            section_count = blog_content.count("## ")
            logger.info(f"博客统计：{word_count}字，{section_count}个主要部分")
        else:
            print(blog_content)

        return 0

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())