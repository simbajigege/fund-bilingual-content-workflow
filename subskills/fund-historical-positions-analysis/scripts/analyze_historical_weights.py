#!/usr/bin/env python3
"""
基金历史持仓权重分析脚本

分析基金多季度持仓数据，计算稳定性指标，识别变动趋势，
生成堆叠图数据和分析报告
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import statistics
from collections import defaultdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HistoricalWeightsAnalyzer:
    """历史持仓权重分析器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化分析器

        Args:
            config: 分析配置
        """
        self.config = config or {
            "stability_thresholds": {
                "high_stability": 85.0,   # 高稳定性阈值
                "medium_stability": 70.0,  # 中等稳定性阈值
                "low_stability": 60.0     # 低稳定性阈值
            },
            "trend_thresholds": {
                "significant_increase": 1.0,  # 显著增加阈值（每季度%）
                "significant_decrease": -1.0,  # 显著减少阈值（每季度%）
                "min_quarters_for_trend": 3   # 判断趋势所需最小季度数
            },
            "weight_thresholds": {
                "min_weight": 0.5,          # 最小权重阈值（%）
                "heavy_weight": 5.0,        # 重仓阈值（%）
                "core_weight": 3.0          # 核心持仓阈值（%）
            },
            "style_classification": {
                "conservative_turnover": 10.0,  # 保守型换手率阈值
                "moderate_turnover": 30.0,      # 适度调整型换手率阈值
                "high_stability": 80.0          # 高稳定性阈值
            }
        }

    def load_data(self, filepath: str) -> Dict[str, Any]:
        """
        从文件加载数据

        Args:
            filepath: 数据文件路径

        Returns:
            加载的数据

        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON解析失败
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"从 {filepath} 加载数据，共 {len(data.get('items', []))} 个季度数据")
            return data

        except FileNotFoundError:
            logger.error(f"文件不存在: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析基金历史持仓数据

        Args:
            data: 基金多季度持仓数据

        Returns:
            分析结果
        """
        items = data.get("items", [])
        fund_code = data.get("master_code", "unknown")

        if not items:
            logger.warning("没有季度数据可分析")
            return {"error": "没有季度数据可分析"}

        logger.info(f"开始分析基金 {fund_code} 的历史持仓数据，共 {len(items)} 个季度")

        # 1. 数据预处理：提取季度权重数据
        quarterly_weights, all_quarters = self._extract_quarterly_weights(items)

        # 2. 对齐和填充时间序列
        aligned_weights = self._align_time_series(quarterly_weights, all_quarters)

        # 3. 归一化权重（确保每季度总和为100%）
        normalized_weights = self._normalize_weights(aligned_weights)

        # 4. 计算各项分析指标
        stability_scores = self._calculate_stability_scores(normalized_weights)
        trend_analysis = self._analyze_weight_trends(normalized_weights)
        new_and_exited = self._identify_new_and_exited_stocks(normalized_weights, all_quarters)
        style_assessment = self._assess_investment_style(normalized_weights, stability_scores)
        key_signals = self._identify_key_signals(normalized_weights, stability_scores, trend_analysis)
        recommendations = self._generate_recommendations(
            normalized_weights, stability_scores, trend_analysis, style_assessment
        )

        # 5. 生成堆叠图数据
        stacked_chart_data = self._generate_stacked_chart_data(normalized_weights, all_quarters)

        # 6. 构建完整报告
        report = self._build_comprehensive_report(
            data=data,
            normalized_weights=normalized_weights,
            stability_scores=stability_scores,
            trend_analysis=trend_analysis,
            new_and_exited=new_and_exited,
            style_assessment=style_assessment,
            key_signals=key_signals,
            recommendations=recommendations,
            stacked_chart_data=stacked_chart_data,
            all_quarters=all_quarters
        )

        logger.info("分析完成")
        return report

    def _extract_quarterly_weights(self, items: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, float]], List[str]]:
        """
        从items中提取季度权重数据

        Args:
            items: 季度数据列表

        Returns:
            (quarterly_weights, all_quarters)
            quarterly_weights: {stock_code: {quarter: weight}}
            all_quarters: 所有季度列表
        """
        quarterly_weights = defaultdict(dict)
        quarter_set = set()

        for item in items:
            as_of_date = item.get("as_of_date")
            if not as_of_date:
                continue

            quarter = self._date_to_quarter(as_of_date)
            if not quarter:
                continue

            quarter_set.add(quarter)

            # 提取所有持仓（A股、美股、港股）
            a_positions = (
                item.get("a_positions", []) +
                item.get("us_positions", []) +
                item.get("hk_positions", [])
            )
            for position in a_positions:
                stock_code = position.get("stock_code")
                weight = position.get("weight", 0)

                if stock_code and weight:
                    quarterly_weights[stock_code][quarter] = weight

        # 按时间排序季度（最近在前）
        all_quarters = sorted(quarter_set, reverse=True)

        logger.info(f"提取了 {len(quarterly_weights)} 只股票在 {len(all_quarters)} 个季度的权重数据")
        return dict(quarterly_weights), all_quarters

    def _date_to_quarter(self, date_str: str) -> Optional[str]:
        """
        将日期字符串转换为季度标识

        Args:
            date_str: 日期字符串，格式为YYYY-MM-DD

        Returns:
            季度标识，如2025Q4
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            month = date_obj.month

            if month in [1, 2, 3]:
                quarter = "Q1"
            elif month in [4, 5, 6]:
                quarter = "Q2"
            elif month in [7, 8, 9]:
                quarter = "Q3"
            else:
                quarter = "Q4"

            return f"{year}{quarter}"
        except (ValueError, TypeError):
            logger.warning(f"日期格式错误，无法转换为季度: {date_str}")
            return None

    def _align_time_series(self, quarterly_weights: Dict[str, Dict[str, float]],
                          all_quarters: List[str]) -> Dict[str, Dict[str, float]]:
        """
        对齐时间序列，填充缺失数据

        Args:
            quarterly_weights: 原始季度权重数据
            all_quarters: 所有季度列表

        Returns:
            对齐后的时间序列数据
        """
        aligned = {}

        for stock_code, weight_data in quarterly_weights.items():
            aligned[stock_code] = {}
            weight_series = []

            for quarter in all_quarters:
                if quarter in weight_data:
                    aligned[stock_code][quarter] = weight_data[quarter]
                    weight_series.append(weight_data[quarter])
                else:
                    # 使用前一个有效值填充（向前填充）
                    prev_value = None
                    for prev_q in all_quarters[all_quarters.index(quarter)+1:]:
                        if prev_q in weight_data:
                            prev_value = weight_data[prev_q]
                            break

                    if prev_value is not None:
                        aligned[stock_code][quarter] = prev_value
                        weight_series.append(prev_value)
                    else:
                        # 如果没有前值，使用0
                        aligned[stock_code][quarter] = 0
                        weight_series.append(0)

            # 检查是否有有效数据
            if max(weight_series) <= 0:
                logger.debug(f"股票 {stock_code} 在所有季度权重为0或缺失，从分析中排除")
                del aligned[stock_code]

        logger.info(f"时间序列对齐完成，共 {len(aligned)} 只股票")
        return aligned

    def _normalize_weights(self, quarterly_weights: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """
        归一化权重，确保每个季度总和为100%

        Args:
            quarterly_weights: 对齐后的权重数据

        Returns:
            归一化后的权重数据
        """
        if not quarterly_weights:
            return {}

        # 获取所有季度
        first_stock = next(iter(quarterly_weights.values()))
        all_quarters = list(first_stock.keys())

        normalized = {}

        for quarter in all_quarters:
            total_weight = sum(
                weight_data.get(quarter, 0)
                for weight_data in quarterly_weights.values()
            )

            if total_weight > 0:
                for stock_code, weight_data in quarterly_weights.items():
                    if stock_code not in normalized:
                        normalized[stock_code] = {}

                    original_weight = weight_data.get(quarter, 0)
                    normalized[stock_code][quarter] = (original_weight / total_weight * 100)

        logger.info(f"权重归一化完成，共 {len(normalized)} 只股票")
        return normalized

    def _calculate_stability_scores(self, normalized_weights: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        计算各股票持仓稳定性评分

        Args:
            normalized_weights: 归一化权重数据

        Returns:
            各股票稳定性评分（0-100）
        """
        stability_scores = {}

        for stock_code, weight_data in normalized_weights.items():
            weights = list(weight_data.values())

            if not weights:
                stability_scores[stock_code] = 0
                continue

            # 1. 计算标准差（越小越好）
            if len(weights) > 1:
                weight_std = statistics.stdev(weights)
            else:
                weight_std = 0

            # 2. 计算变动率
            min_weight = min(weights)
            max_weight = max(weights)
            avg_weight = statistics.mean(weights)

            if avg_weight > 0:
                change_rate = (max_weight - min_weight) / avg_weight * 100
            else:
                change_rate = 0

            # 3. 计算连续性（连续非零季度比例）
            non_zero_quarters = sum(1 for w in weights if w > 0.1)
            continuity_ratio = non_zero_quarters / len(weights) * 100

            # 4. 综合评分
            # 标准差分数（标准差越小分数越高）
            std_score = max(0, 100 - weight_std * 5)

            # 变动率分数（变动率越小分数越高）
            change_score = max(0, 100 - change_rate)

            # 连续性分数
            continuity_score = continuity_ratio

            # 加权计算综合稳定性分数
            stability_score = (
                std_score * 0.4 +
                change_score * 0.3 +
                continuity_score * 0.3
            )

            stability_scores[stock_code] = stability_score

        logger.info(f"稳定性评分计算完成，共 {len(stability_scores)} 只股票")
        return stability_scores

    def _analyze_weight_trends(self, normalized_weights: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """
        分析权重变化趋势

        Args:
            normalized_weights: 归一化权重数据

        Returns:
            各股票趋势分析结果
        """
        trend_analysis = {}

        for stock_code, weight_data in normalized_weights.items():
            # 按时间顺序获取权重序列（最近在前需要反转）
            quarters = sorted(weight_data.keys(), reverse=True)  # 确保最近在前
            weights = [weight_data[q] for q in quarters]

            if len(weights) < 2:
                trend_analysis[stock_code] = {
                    "trend": "insufficient_data",
                    "trend_strength": 0,
                    "quarters_analyzed": len(weights)
                }
                continue

            # 计算简单线性回归斜率
            n = len(weights)
            x = list(range(n))
            y = weights

            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x_i * y_i for x_i, y_i in zip(x, y))
            sum_x2 = sum(x_i * x_i for x_i in x)

            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            else:
                slope = 0

            # 判断趋势类型
            if slope > self.config["trend_thresholds"]["significant_increase"]:
                trend = "increasing"
                trend_strength = "strong" if slope > 2.0 else "moderate"
            elif slope < self.config["trend_thresholds"]["significant_decrease"]:
                trend = "decreasing"
                trend_strength = "strong" if slope < -2.0 else "moderate"
            else:
                trend = "stable"
                trend_strength = "weak"

            # 计算趋势强度数值
            trend_strength_value = abs(slope)

            # 最近季度变化
            recent_change = weights[0] - weights[1] if len(weights) > 1 else 0

            trend_analysis[stock_code] = {
                "trend": trend,
                "trend_strength": trend_strength,
                "trend_strength_value": round(trend_strength_value, 2),
                "slope": round(slope, 3),
                "recent_change": round(recent_change, 2),
                "quarters_analyzed": n,
                "current_weight": round(weights[0], 2),
                "avg_weight": round(statistics.mean(weights), 2)
            }

        logger.info(f"趋势分析完成，共 {len(trend_analysis)} 只股票")
        return trend_analysis

    def _identify_new_and_exited_stocks(self, normalized_weights: Dict[str, Dict[str, float]],
                                       all_quarters: List[str]) -> Dict[str, List[str]]:
        """
        识别新进和退出的股票

        Args:
            normalized_weights: 归一化权重数据
            all_quarters: 所有季度列表（最近在前）

        Returns:
            {"new_stocks": [], "exited_stocks": []}
        """
        if len(all_quarters) < 2:
            return {"new_stocks": [], "exited_stocks": []}

        # 最近2个季度视为"最近"
        recent_quarters = all_quarters[:2]
        previous_quarters = all_quarters[2:]

        stocks_in_recent = set()
        stocks_in_previous = set()

        for stock_code, weight_data in normalized_weights.items():
            # 检查最近季度
            for quarter in recent_quarters:
                if quarter in weight_data and weight_data[quarter] > 0.1:
                    stocks_in_recent.add(stock_code)
                    break

            # 检查之前季度
            for quarter in previous_quarters:
                if quarter in weight_data and weight_data[quarter] > 0.1:
                    stocks_in_previous.add(stock_code)
                    break

        # 新进股票：在最近季度出现但之前季度未出现
        new_stocks = list(stocks_in_recent - stocks_in_previous)

        # 退出股票：在之前季度出现但最近季度未出现
        exited_stocks = list(stocks_in_previous - stocks_in_recent)

        logger.info(f"识别出 {len(new_stocks)} 只新进股票，{len(exited_stocks)} 只退出股票")
        return {
            "new_stocks": new_stocks,
            "exited_stocks": exited_stocks
        }

    def _assess_investment_style(self, normalized_weights: Dict[str, Dict[str, float]],
                                stability_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        评估投资风格

        Args:
            normalized_weights: 归一化权重数据
            stability_scores: 稳定性评分

        Returns:
            投资风格评估结果
        """
        if not normalized_weights or not stability_scores:
            return {"type": "unknown", "characteristics": [], "suitability": "unknown"}

        # 计算平均稳定性评分
        avg_stability = statistics.mean(stability_scores.values()) if stability_scores else 0

        # 计算季度换手率（简化版）
        all_quarters = sorted(list(next(iter(normalized_weights.values())).keys()))
        turnover_rate = self._calculate_turnover_rate(normalized_weights, all_quarters)

        # 计算集中度
        concentration_ratio = self._calculate_concentration_ratio(normalized_weights)

        # 分类投资风格
        style = self._classify_investment_style(turnover_rate, avg_stability, concentration_ratio)

        return style

    def _calculate_turnover_rate(self, normalized_weights: Dict[str, Dict[str, float]],
                                all_quarters: List[str]) -> float:
        """
        计算季度换手率

        Args:
            normalized_weights: 归一化权重数据
            all_quarters: 所有季度列表

        Returns:
            平均季度换手率（%）
        """
        if len(all_quarters) < 2:
            return 0

        turnover_rates = []

        for i in range(len(all_quarters) - 1):
            current_q = all_quarters[i]
            next_q = all_quarters[i + 1]

            # 获取两个季度的持仓股票集合
            current_stocks = {
                stock for stock, weight_data in normalized_weights.items()
                if current_q in weight_data and weight_data[current_q] > 0.1
            }
            next_stocks = {
                stock for stock, weight_data in normalized_weights.items()
                if next_q in weight_data and weight_data[next_q] > 0.1
            }

            # 计算变动股票的比例
            changed_stocks = (current_stocks - next_stocks) | (next_stocks - current_stocks)
            total_stocks = len(current_stocks | next_stocks)

            if total_stocks > 0:
                turnover_rate = len(changed_stocks) / total_stocks * 100
                turnover_rates.append(turnover_rate)

        if turnover_rates:
            return statistics.mean(turnover_rates)
        else:
            return 0

    def _calculate_concentration_ratio(self, normalized_weights: Dict[str, Dict[str, float]]) -> float:
        """
        计算持仓集中度（前5大持仓权重占比）

        Args:
            normalized_weights: 归一化权重数据

        Returns:
            前5大持仓集中度（%）
        """
        if not normalized_weights:
            return 0

        # 计算平均权重
        avg_weights = {}
        for stock_code, weight_data in normalized_weights.items():
            weights = list(weight_data.values())
            if weights:
                avg_weights[stock_code] = statistics.mean(weights)

        # 按平均权重排序
        sorted_stocks = sorted(avg_weights.items(), key=lambda x: x[1], reverse=True)

        # 计算前5大权重总和
        top5_sum = sum(weight for _, weight in sorted_stocks[:5])
        total_sum = sum(avg_weights.values())

        if total_sum > 0:
            return top5_sum / total_sum * 100
        else:
            return 0

    def _classify_investment_style(self, turnover_rate: float, avg_stability: float,
                                  concentration_ratio: float) -> Dict[str, Any]:
        """
        分类投资风格

        Args:
            turnover_rate: 季度换手率
            avg_stability: 平均稳定性评分
            concentration_ratio: 前5大持仓集中度

        Returns:
            风格分类结果
        """
        style = {
            "type": "unknown",
            "characteristics": [],
            "suitability": "unknown",
            "tracking_difficulty": "unknown",
            "turnover_rate": round(turnover_rate, 1),
            "avg_stability": round(avg_stability, 1),
            "concentration_ratio": round(concentration_ratio, 1)
        }

        if turnover_rate < self.config["style_classification"]["conservative_turnover"] and avg_stability > self.config["style_classification"]["high_stability"]:
            style["type"] = "conservative_stable"
            style["characteristics"] = [
                "持仓结构长期稳定",
                "换手率低",
                "核心持仓明确",
                "投资逻辑一致"
            ]
            style["suitability"] = "high"
            style["tracking_difficulty"] = "低"
            style["interpretation"] = "风格保守稳定，适合普通投资者跟踪"

        elif turnover_rate < self.config["style_classification"]["moderate_turnover"] and avg_stability > 60:
            style["type"] = "moderate_adjustment"
            style["characteristics"] = [
                "适度调整持仓",
                "换手率中等",
                "有核心持仓也有灵活调整",
                "根据市场适度优化"
            ]
            style["suitability"] = "medium"
            style["tracking_difficulty"] = "中"
            style["interpretation"] = "风格适度调整，需要一定分析能力"

        else:
            style["type"] = "active_trading"
            style["characteristics"] = [
                "频繁调整持仓",
                "换手率高",
                "持仓结构变化大",
                "投资逻辑可能变化"
            ]
            style["suitability"] = "low"
            style["tracking_difficulty"] = "高"
            style["interpretation"] = "风格积极交易，普通投资者跟踪困难"

        # 添加集中度特征
        if concentration_ratio > 60:
            style["characteristics"].append("持仓高度集中（前5大>60%）")
        elif concentration_ratio > 40:
            style["characteristics"].append("持仓适度集中（前5大40-60%）")
        else:
            style["characteristics"].append("持仓相对分散（前5大<40%）")

        return style

    def _identify_key_signals(self, normalized_weights: Dict[str, Dict[str, float]],
                             stability_scores: Dict[str, float],
                             trend_analysis: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        识别关键信号

        Args:
            normalized_weights: 归一化权重数据
            stability_scores: 稳定性评分
            trend_analysis: 趋势分析结果

        Returns:
            关键信号列表
        """
        key_signals = []

        for stock_code, weight_data in normalized_weights.items():
            weights = list(weight_data.values())
            if not weights:
                continue

            avg_weight = statistics.mean(weights)
            stability = stability_scores.get(stock_code, 0)
            trend_info = trend_analysis.get(stock_code, {})
            trend = trend_info.get("trend", "stable")

            # 信号1：高稳定性核心持仓
            if (avg_weight >= self.config["weight_thresholds"]["core_weight"] and
                stability >= self.config["stability_thresholds"]["high_stability"]):
                key_signals.append({
                    "stock_code": stock_code,
                    "signal_type": "core_holding_high_stability",
                    "description": f"核心持仓，平均权重{avg_weight:.1f}%，稳定性{stability:.1f}分",
                    "priority": "P0",
                    "avg_weight": round(avg_weight, 2),
                    "stability_score": round(stability, 1),
                    "content_angle": "长期稳定持仓，适合普通投资者跟踪"
                })

            # 信号2：持续加仓趋势
            elif (trend == "increasing" and
                  avg_weight >= self.config["weight_thresholds"]["heavy_weight"]):
                slope = trend_info.get("slope", 0)
                key_signals.append({
                    "stock_code": stock_code,
                    "signal_type": "continuous_increasing",
                    "description": f"持续加仓趋势，平均权重{avg_weight:.1f}%，季度斜率{slope:.3f}",
                    "priority": "P1",
                    "avg_weight": round(avg_weight, 2),
                    "trend_slope": round(slope, 3),
                    "content_angle": "基金经理持续看好，主动加仓逻辑分析"
                })

            # 信号3：高波动性持仓
            elif (stability < self.config["stability_thresholds"]["low_stability"] and
                  avg_weight >= self.config["weight_thresholds"]["core_weight"]):
                key_signals.append({
                    "stock_code": stock_code,
                    "signal_type": "high_volatility",
                    "description": f"高波动性持仓，稳定性仅{stability:.1f}分",
                    "priority": "P2",
                    "avg_weight": round(avg_weight, 2),
                    "stability_score": round(stability, 1),
                    "content_angle": "波动较大，跟踪难度高，需注意风险"
                })

        # 按优先级排序
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        key_signals.sort(key=lambda x: priority_order.get(x["priority"], 4))

        logger.info(f"识别出 {len(key_signals)} 个关键信号")
        return key_signals

    def _generate_recommendations(self, normalized_weights: Dict[str, Dict[str, float]],
                                 stability_scores: Dict[str, float],
                                 trend_analysis: Dict[str, Dict[str, Any]],
                                 style_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成投资建议

        Args:
            normalized_weights: 归一化权重数据
            stability_scores: 稳定性评分
            trend_analysis: 趋势分析结果
            style_assessment: 风格评估结果

        Returns:
            投资建议
        """
        recommendations = {
            "immediate_actions": [],
            "watch_list": [],
            "risk_warnings": []
        }

        # 基于关键信号生成即时行动
        core_holdings = [
            stock for stock, score in stability_scores.items()
            if score >= self.config["stability_thresholds"]["high_stability"]
        ]

        if core_holdings:
            core_names = list(core_holdings)[:3]
            recommendations["immediate_actions"].append(
                f"重点分析核心持仓（如{', '.join(core_names)}）的长期投资逻辑"
            )

        # 基于趋势生成关注列表
        increasing_stocks = [
            stock for stock, info in trend_analysis.items()
            if info.get("trend") == "increasing"
        ]

        for stock in increasing_stocks[:2]:
            info = trend_analysis[stock]
            recommendations["watch_list"].append({
                "stock_code": stock,
                "reason": f"持续加仓趋势，斜率{info.get('slope', 0):.3f}",
                "monitoring_points": ["季度财报业绩", "行业政策变化", "技术面突破"]
            })

        # 基于风格生成风险提示
        style_type = style_assessment.get("type", "")
        if style_type == "active_trading":
            recommendations["risk_warnings"].append(
                "投资风格积极，持仓变动频繁，普通投资者跟踪困难"
            )

        turnover_rate = style_assessment.get("turnover_rate", 0)
        if turnover_rate > 30:
            recommendations["risk_warnings"].append(
                f"季度换手率较高（{turnover_rate:.1f}%），需注意13F数据45天滞后性影响"
            )

        # 通用风险提示
        recommendations["risk_warnings"].append(
            "本文分析基于历史数据，不构成投资建议，投资需谨慎"
        )

        return recommendations

    def _generate_stacked_chart_data(self, normalized_weights: Dict[str, Dict[str, float]],
                                    all_quarters: List[str]) -> List[Dict[str, Any]]:
        """
        生成堆叠图数据

        Args:
            normalized_weights: 归一化权重数据
            all_quarters: 所有季度列表

        Returns:
            堆叠图数据列表
        """
        stacked_data = []
        min_weight = self.config["weight_thresholds"]["min_weight"]

        for quarter in all_quarters:
            for stock_code, weight_data in normalized_weights.items():
                weight = weight_data.get(quarter, 0)

                if weight >= min_weight:
                    stacked_data.append({
                        "quarter": quarter,
                        "ticker": stock_code,
                        "portfolio_weight_pct": round(weight, 2)
                    })

        # 按季度和权重排序
        stacked_data.sort(key=lambda x: (x["quarter"], -x["portfolio_weight_pct"]))

        logger.info(f"生成堆叠图数据 {len(stacked_data)} 条记录")
        return stacked_data

    def _build_comprehensive_report(self, **kwargs) -> Dict[str, Any]:
        """
        构建综合分析报告

        Args:
            **kwargs: 各种分析结果

        Returns:
            完整分析报告
        """
        data = kwargs.get("data", {})
        normalized_weights = kwargs.get("normalized_weights", {})
        stability_scores = kwargs.get("stability_scores", {})
        trend_analysis = kwargs.get("trend_analysis", {})
        new_and_exited = kwargs.get("new_and_exited", {})
        style_assessment = kwargs.get("style_assessment", {})
        key_signals = kwargs.get("key_signals", [])
        recommendations = kwargs.get("recommendations", {})
        stacked_chart_data = kwargs.get("stacked_chart_data", [])
        all_quarters = kwargs.get("all_quarters", [])

        # 提取股票名称信息
        stock_names = {}
        items = data.get("items", [])
        for item in items:
            all_positions = (
                item.get("a_positions", []) +
                item.get("us_positions", []) +
                item.get("hk_positions", [])
            )
            for position in all_positions:
                stock_code = position.get("stock_code")
                stock_name = position.get("stock_name")
                if stock_code and stock_name:
                    stock_names[stock_code] = stock_name

        # 为关键信号添加股票名称
        for signal in key_signals:
            stock_code = signal.get("stock_code")
            if stock_code in stock_names:
                signal["stock_name"] = stock_names[stock_code]

        # 构建报告
        report = {
            "metadata": {
                "fund_code": data.get("master_code", "unknown"),
                "fund_name": items[0].get("master_name", "unknown") if items else "unknown",
                "analysis_date": datetime.now().isoformat(),
                "quarters_analyzed": all_quarters,
                "unique_stocks": len(normalized_weights),
                "total_positions": sum(len(w) for w in normalized_weights.values()),
                "analysis_version": "1.0.0",
                "min_weight_threshold": self.config["weight_thresholds"]["min_weight"]
            },
            "stability_analysis": {
                "overall_stability_score": round(statistics.mean(stability_scores.values()) if stability_scores else 0, 1),
                "high_stability_stocks": self._get_high_stability_stocks(stability_scores, normalized_weights, stock_names),
                "high_volatility_stocks": self._get_high_volatility_stocks(stability_scores, normalized_weights, stock_names),
                "quarterly_turnover_rate": style_assessment.get("turnover_rate", 0)
            },
            "trend_analysis": {
                "increasing_trend_stocks": self._get_trend_stocks(trend_analysis, "increasing", normalized_weights, stock_names),
                "decreasing_trend_stocks": self._get_trend_stocks(trend_analysis, "decreasing", normalized_weights, stock_names),
                "new_entrants": new_and_exited.get("new_stocks", []),
                "exited_stocks": new_and_exited.get("exited_stocks", [])
            },
            "style_assessment": style_assessment,
            "key_signals": key_signals,
            "recommendations": recommendations,
            "stacked_chart_data_summary": {
                "total_records": len(stacked_chart_data),
                "quarters_count": len(all_quarters),
                "stocks_count": len(normalized_weights),
                "avg_weight_per_quarter": 100.0,
                "max_weight_single_stock": self._get_max_weight(normalized_weights),
                "min_weight_included": self.config["weight_thresholds"]["min_weight"]
            }
        }

        return report

    def _get_high_stability_stocks(self, stability_scores: Dict[str, float],
                                  normalized_weights: Dict[str, Dict[str, float]],
                                  stock_names: Dict[str, str]) -> List[Dict[str, Any]]:
        """获取高稳定性股票"""
        threshold = self.config["stability_thresholds"]["high_stability"]
        high_stability = []

        for stock_code, score in stability_scores.items():
            if score >= threshold:
                weight_data = normalized_weights.get(stock_code, {})
                weights = list(weight_data.values())
                if weights:
                    high_stability.append({
                        "stock_code": stock_code,
                        "stock_name": stock_names.get(stock_code, stock_code),
                        "stability_score": round(score, 1),
                        "avg_weight": round(statistics.mean(weights), 2),
                        "weight_std": round(statistics.stdev(weights) if len(weights) > 1 else 0, 2),
                        "max_weight": round(max(weights), 2),
                        "min_weight": round(min(weights), 2)
                    })

        # 按稳定性评分降序排序
        high_stability.sort(key=lambda x: x["stability_score"], reverse=True)
        return high_stability[:5]  # 返回前5个

    def _get_high_volatility_stocks(self, stability_scores: Dict[str, float],
                                   normalized_weights: Dict[str, Dict[str, float]],
                                   stock_names: Dict[str, str]) -> List[Dict[str, Any]]:
        """获取高波动性股票"""
        threshold = self.config["stability_thresholds"]["low_stability"]
        high_volatility = []

        for stock_code, score in stability_scores.items():
            if score < threshold:
                weight_data = normalized_weights.get(stock_code, {})
                weights = list(weight_data.values())
                if weights and statistics.mean(weights) >= self.config["weight_thresholds"]["core_weight"]:
                    high_volatility.append({
                        "stock_code": stock_code,
                        "stock_name": stock_names.get(stock_code, stock_code),
                        "stability_score": round(score, 1),
                        "avg_weight": round(statistics.mean(weights), 2),
                        "weight_std": round(statistics.stdev(weights) if len(weights) > 1 else 0, 2),
                        "volatility_reason": "权重波动较大，季度间调整频繁"
                    })

        # 按稳定性评分升序排序（波动性越大分数越低）
        high_volatility.sort(key=lambda x: x["stability_score"])
        return high_volatility[:3]  # 返回前3个

    def _get_trend_stocks(self, trend_analysis: Dict[str, Dict[str, Any]], trend_type: str,
                         normalized_weights: Dict[str, Dict[str, float]],
                         stock_names: Dict[str, str]) -> List[Dict[str, Any]]:
        """获取特定趋势类型的股票"""
        trend_stocks = []

        for stock_code, info in trend_analysis.items():
            if info.get("trend") == trend_type:
                weight_data = normalized_weights.get(stock_code, {})
                weights = list(weight_data.values())
                if weights:
                    current_weight = info.get("current_weight", 0)
                    slope = info.get("slope", 0)
                    trend_strength = info.get("trend_strength", "")

                    trend_stocks.append({
                        "stock_code": stock_code,
                        "stock_name": stock_names.get(stock_code, stock_code),
                        "current_weight": current_weight,
                        "weight_change": round(slope * (len(weights) - 1), 2),  # 总变化
                        "trend_strength": trend_strength,
                        "slope": round(slope, 3),
                        "avg_weight": round(statistics.mean(weights), 2)
                    })

        # 按变化幅度降序排序
        if trend_type == "increasing":
            trend_stocks.sort(key=lambda x: x["weight_change"], reverse=True)
        else:  # decreasing
            trend_stocks.sort(key=lambda x: x["weight_change"])

        return trend_stocks[:5]  # 返回前5个

    def _get_max_weight(self, normalized_weights: Dict[str, Dict[str, float]]) -> float:
        """获取单只股票的最大权重"""
        max_weight = 0
        for weight_data in normalized_weights.values():
            for weight in weight_data.values():
                if weight > max_weight:
                    max_weight = weight
        return round(max_weight, 2)

    def generate_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        生成自然语言总结

        Args:
            analysis_results: 分析结果

        Returns:
            自然语言总结
        """
        metadata = analysis_results.get("metadata", {})
        stability = analysis_results.get("stability_analysis", {})
        trend = analysis_results.get("trend_analysis", {})
        style = analysis_results.get("style_assessment", {})
        key_signals = analysis_results.get("key_signals", [])
        recommendations = analysis_results.get("recommendations", {})

        # 构建总结
        summary_parts = []

        # 1. 分析概况
        fund_code = metadata.get("fund_code", "unknown")
        fund_name = metadata.get("fund_name", "unknown")
        quarters = metadata.get("quarters_analyzed", [])
        unique_stocks = metadata.get("unique_stocks", 0)

        summary_parts.append(f"【基金历史持仓权重分析报告 - {fund_code}({fund_name})】\n")
        summary_parts.append(f"一、分析概况")
        summary_parts.append(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_parts.append(f"分析季度：{len(quarters)}个（{quarters[0]} 至 {quarters[-1]}）")
        summary_parts.append(f"分析股票：{unique_stocks}只\n")

        # 2. 稳定性分析
        overall_stability = stability.get("overall_stability_score", 0)
        high_stability = stability.get("high_stability_stocks", [])
        turnover_rate = stability.get("quarterly_turnover_rate", 0)

        stability_text = f"整体稳定性评分：{overall_stability}/100"
        if overall_stability >= 80:
            stability_text += "（持仓较为稳定）"
        elif overall_stability >= 60:
            stability_text += "（持仓适度稳定）"
        else:
            stability_text += "（持仓波动较大）"

        summary_parts.append(f"二、持仓稳定性分析")
        summary_parts.append(stability_text)
        summary_parts.append(f"季度换手率：{turnover_rate:.1f}%")

        if high_stability:
            stock_names = [s.get("stock_name", s.get("stock_code")) for s in high_stability[:3]]
            summary_parts.append(f"高稳定性核心持仓：{', '.join(stock_names)}\n")

        # 3. 变动趋势分析
        increasing = trend.get("increasing_trend_stocks", [])
        decreasing = trend.get("decreasing_trend_stocks", [])
        new_entrants = trend.get("new_entrants", [])
        exited_stocks = trend.get("exited_stocks", [])

        summary_parts.append(f"三、变动趋势分析")
        if increasing:
            stock_names = [s.get("stock_name", s.get("stock_code")) for s in increasing[:2]]
            summary_parts.append(f"持续加仓：{', '.join(stock_names)}")

        if decreasing:
            stock_names = [s.get("stock_name", s.get("stock_code")) for s in decreasing[:2]]
            summary_parts.append(f"持续减仓：{', '.join(stock_names)}")

        if new_entrants:
            summary_parts.append(f"新进持仓：{len(new_entrants)}只")

        if exited_stocks:
            summary_parts.append(f"退出持仓：{len(exited_stocks)}只")
        summary_parts.append("")

        # 4. 投资风格评估
        style_type = style.get("type", "unknown")
        style_interpretation = style.get("interpretation", "")
        suitability = style.get("suitability", "unknown")
        difficulty = style.get("tracking_difficulty", "unknown")

        summary_parts.append(f"四、投资风格评估")
        summary_parts.append(f"风格类型：{style_type}")
        summary_parts.append(f"风格解读：{style_interpretation}")
        summary_parts.append(f"适合跟踪程度：{suitability}")
        summary_parts.append(f"跟踪难度：{difficulty}\n")

        # 5. 关键信号
        summary_parts.append(f"五、关键信号")
        if key_signals:
            for i, signal in enumerate(key_signals[:3]):  # 只显示前3个
                stock_name = signal.get("stock_name", signal.get("stock_code"))
                desc = signal.get("description", "")
                priority = signal.get("priority", "")
                summary_parts.append(f"{i+1}. [{priority}] {stock_name}：{desc}")
        else:
            summary_parts.append("未发现显著关键信号")
        summary_parts.append("")

        # 6. 投资建议
        immediate_actions = recommendations.get("immediate_actions", [])
        risk_warnings = recommendations.get("risk_warnings", [])

        summary_parts.append(f"六、投资建议")
        if immediate_actions:
            summary_parts.append(f"重点关注：{immediate_actions[0]}")

        if risk_warnings:
            summary_parts.append(f"风险提示：{risk_warnings[0]}")

        # 7. 报告信息
        summary_parts.append("")
        summary_parts.append(f"报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_parts.append("数据来源：ai2alpha.cn基金多季度持仓数据")
        summary_parts.append("免责声明：本文为数据分析，不构成投资建议")

        return "\n".join(summary_parts)

    def save_stacked_chart_data(self, stacked_chart_data: List[Dict[str, Any]],
                               filepath: str) -> None:
        """
        保存堆叠图数据到CSV文件

        Args:
            stacked_chart_data: 堆叠图数据
            filepath: 输出文件路径
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ["quarter", "ticker", "portfolio_weight_pct"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(stacked_chart_data)
            logger.info(f"堆叠图数据已保存到: {filepath}")
        except IOError as e:
            logger.error(f"保存CSV文件失败: {e}")
            raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='分析基金历史持仓权重')
    parser.add_argument('--input', '-i', required=True, help='输入JSON文件路径')
    parser.add_argument('--output', '-o', help='结构化报告输出路径（JSON格式）')
    parser.add_argument('--summary-text', '-s', help='自然语言总结输出路径')
    parser.add_argument('--stacked-data', '-d', help='堆叠图数据输出路径（CSV格式）')
    parser.add_argument('--verbose', action='store_true', help='输出详细信息')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # 初始化分析器
        analyzer = HistoricalWeightsAnalyzer()

        # 加载数据
        logger.info(f"加载数据: {args.input}")
        data = analyzer.load_data(args.input)

        # 分析数据
        logger.info("开始分析数据...")
        analysis_results = analyzer.analyze(data)

        # 生成自然语言总结
        logger.info("生成自然语言总结...")
        summary = analyzer.generate_summary(analysis_results)

        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            logger.info(f"结构化报告已保存: {args.output}")

        if args.summary_text:
            with open(args.summary_text, 'w', encoding='utf-8') as f:
                f.write(summary)
            logger.info(f"自然语言总结已保存: {args.summary_text}")

        if args.stacked_data and "stacked_chart_data" in analysis_results:
            stacked_data = analysis_results.get("stacked_chart_data", [])
            analyzer.save_stacked_chart_data(stacked_data, args.stacked_data)

        # 控制台输出
        if not args.output and not args.summary_text and not args.stacked_data:
            print(summary)

        # 输出关键信息
        metadata = analysis_results.get("metadata", {})
        stability = analysis_results.get("stability_analysis", {})
        style = analysis_results.get("style_assessment", {})

        fund_code = metadata.get("fund_code", "unknown")
        overall_stability = stability.get("overall_stability_score", 0)
        style_type = style.get("type", "unknown")
        turnover_rate = style.get("turnover_rate", 0)

        print(f"\n分析完成!")
        print(f"基金代码: {fund_code}")
        print(f"整体稳定性: {overall_stability}/100")
        print(f"投资风格: {style_type} (换手率: {turnover_rate:.1f}%)")

        # 显示关键信号
        key_signals = analysis_results.get("key_signals", [])
        if key_signals:
            print(f"\n关键信号 ({len(key_signals)} 个):")
            for i, signal in enumerate(key_signals[:3]):
                stock_name = signal.get("stock_name", signal.get("stock_code"))
                desc = signal.get("description", "")
                print(f"  {i+1}. {stock_name}: {desc}")

        return 0

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())