#!/usr/bin/env python3
"""
基金持仓数据分析脚本

分析基金持仓热力图数据，生成结构化报告和自然语言总结
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FundHeatmapAnalyzer:
    """基金热力图数据分析器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化分析器

        Args:
            config: 分析配置
        """
        self.config = config or {
            "heatmap_thresholds": {
                "heavy_weight": 5.0,    # 大色块阈值（%）
                "light_weight": 2.0,    # 小色块阈值（%）
                "red_percentage": 30.0  # 整体偏红阈值（%）
            },
            "financial_thresholds": {
                "low_pe": 15.0,         # 低PE阈值
                "low_pb": 1.5,          # 低PB阈值
                "high_turnover": 3.0,   # 高换手率阈值（%）
                "strong_change": 2.0    # 强势涨幅阈值（%）
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

            if not data.get("success"):
                logger.warning("数据中的success字段为false")

            logger.info(f"从 {filepath} 加载数据，共 {len(data.get('data', []))} 条记录")
            return data

        except FileNotFoundError:
            logger.error(f"文件不存在: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析基金持仓数据

        Args:
            data: 基金持仓数据

        Returns:
            分析结果
        """
        stocks = data.get("data", [])
        meta = data.get("meta", {})

        if not stocks:
            logger.warning("没有持仓数据可分析")
            return {}

        logger.info(f"开始分析 {len(stocks)} 只持仓股票")

        # 执行各项分析
        heatmap_signals = self._analyze_heatmap_signals(stocks)
        overall_color = self._analyze_overall_color(stocks)
        financial_analysis = self._analyze_financials(stocks)
        ai_advice_summary = self._analyze_ai_advice(stocks)
        industry_distribution = self._analyze_industry_distribution(stocks)
        portfolio_score = self._calculate_portfolio_score(stocks, {
            "heatmap_signals": heatmap_signals,
            "overall_color": overall_color
        })
        top_signals = self._identify_top_signals(stocks, heatmap_signals, ai_advice_summary)
        recommendations = self._generate_recommendations(stocks, heatmap_signals, overall_color, portfolio_score)

        # 构建完整报告
        report = {
            "metadata": {
                "fund_code": meta.get("master_code", "unknown"),
                "analysis_date": datetime.now().isoformat(),
                "data_collection_time": stocks[0].get("collection_time") if stocks else None,
                "total_stocks": len(stocks),
                "total_selected_codes": meta.get("total_selected_codes", 0),
                "analysis_version": "1.0.0"
            },
            "heatmap_signals": heatmap_signals,
            "overall_color": overall_color,
            "financial_analysis": financial_analysis,
            "ai_advice_summary": ai_advice_summary,
            "industry_distribution": industry_distribution,
            "portfolio_score": portfolio_score,
            "top_signals": top_signals,
            "recommendations": recommendations
        }

        logger.info("分析完成")
        return report

    def _analyze_heatmap_signals(self, stocks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        分析热力图信号

        Args:
            stocks: 股票列表

        Returns:
            热力图信号分类
        """
        heavy_thresh = self.config["heatmap_thresholds"]["heavy_weight"]
        light_thresh = self.config["heatmap_thresholds"]["light_weight"]

        signals = {
            "strong_buy_heavy": [],  # 大色块+绿色
            "strong_sell_heavy": [], # 大色块+红色
            "strong_buy_light": [],  # 小色块+绿色
            "neutral_heavy": [],     # 大色块+黄色
            "neutral_light": [],     # 小色块+黄色
            "strong_sell_light": []  # 小色块+红色
        }

        for stock in stocks:
            weight = stock.get("weight", 0)
            action = stock.get("analysis_summary", {}).get("action", "持有")

            # 确定权重级别
            if weight > heavy_thresh:
                weight_level = "heavy"
            elif weight < light_thresh:
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
            signal_key_mapping = {
                "green_heavy": "strong_buy_heavy",
                "red_heavy": "strong_sell_heavy",
                "green_light": "strong_buy_light",
                "yellow_heavy": "neutral_heavy",
                "yellow_light": "neutral_light",
                "red_light": "strong_sell_light",
            }

            mapped_key = signal_key_mapping.get(signal_key)
            if mapped_key:
                signals[mapped_key].append(self._create_stock_summary(stock))

        logger.info(f"热力图信号分析完成: {sum(len(v) for v in signals.values())} 个关键信号")
        return signals

    def _analyze_overall_color(self, stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析整体颜色

        Args:
            stocks: 股票列表

        Returns:
            整体颜色分析结果
        """
        total = len(stocks)
        if total == 0:
            return {"is_red": False, "red_percentage": 0}

        red_count = 0
        for stock in stocks:
            action = stock.get("analysis_summary", {}).get("action", "持有")
            if action in ["卖出", "强力卖出"]:
                red_count += 1

        red_percentage = (red_count / total) * 100
        is_red = red_percentage > self.config["heatmap_thresholds"]["red_percentage"]

        interpretation = "整体持仓偏中性"
        if is_red:
            interpretation = f"整体持仓偏红，{red_percentage:.1f}%的股票被AI看空"
        elif red_percentage > 0:
            interpretation = f"整体持仓偏绿，仅{red_percentage:.1f}%的股票被AI看空"

        return {
            "is_red": is_red,
            "red_percentage": red_percentage,
            "red_count": red_count,
            "total_count": total,
            "color_interpretation": interpretation
        }

    def _analyze_financials(self, stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析财务指标

        Args:
            stocks: 股票列表

        Returns:
            财务分析结果
        """
        # 估值分析
        pe_ratios = [s.get("pe_ratio") for s in stocks if s.get("pe_ratio") is not None]
        pb_ratios = [s.get("pb_ratio") for s in stocks if s.get("pb_ratio") is not None]

        # 动量分析
        changes = [s.get("change_pct", 0) for s in stocks]
        amplitudes = [s.get("amplitude", 0) for s in stocks]

        # 流动性分析
        turnovers = [s.get("turnover_rate", 0) for s in stocks]

        # 识别低估值股票
        low_pe_thresh = self.config["financial_thresholds"]["low_pe"]
        low_pb_thresh = self.config["financial_thresholds"]["low_pb"]
        high_turnover_thresh = self.config["financial_thresholds"]["high_turnover"]
        strong_change_thresh = self.config["financial_thresholds"]["strong_change"]

        low_pe_stocks = []
        low_pb_stocks = []
        high_liquidity_stocks = []
        strong_stocks = []

        for stock in stocks:
            # 低PE股票
            pe = stock.get("pe_ratio")
            if pe is not None and pe < low_pe_thresh:
                low_pe_stocks.append(self._create_stock_summary(stock))

            # 低PB股票
            pb = stock.get("pb_ratio")
            if pb is not None and pb < low_pb_thresh:
                low_pb_stocks.append(self._create_stock_summary(stock))

            # 高流动性股票
            turnover = stock.get("turnover_rate", 0)
            if turnover > high_turnover_thresh:
                high_liquidity_stocks.append(self._create_stock_summary(stock))

            # 强势股票
            change = stock.get("change_pct", 0)
            if change > strong_change_thresh:
                strong_stocks.append(self._create_stock_summary(stock))

        return {
            "valuation_summary": {
                "pe_stats": self._calculate_stats(pe_ratios) if pe_ratios else None,
                "pb_stats": self._calculate_stats(pb_ratios) if pb_ratios else None,
                "low_pe_stocks": low_pe_stocks[:5],
                "low_pb_stocks": low_pb_stocks[:5]
            },
            "momentum_summary": {
                "avg_change": sum(changes)/len(changes) if changes else 0,
                "max_change": max(changes) if changes else 0,
                "min_change": min(changes) if changes else 0,
                "avg_amplitude": sum(amplitudes)/len(amplitudes) if amplitudes else 0,
                "strong_stocks": strong_stocks[:5]
            },
            "liquidity_summary": {
                "avg_turnover": sum(turnovers)/len(turnovers) if turnovers else 0,
                "high_liquidity_stocks": high_liquidity_stocks[:5]
            }
        }

    def _analyze_ai_advice(self, stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析AI投资建议

        Args:
            stocks: 股票列表

        Returns:
            AI建议分析结果
        """
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

        confidences = []
        risk_scores = []
        price_gaps = []

        for stock in stocks:
            analysis = stock.get("analysis_summary", {})
            action = analysis.get("action", "持有")
            weight = stock.get("weight", 0)

            # 统计操作建议
            if action in action_count:
                action_count[action] += 1
                total_weight_by_action[action] += weight

            # 收集置信度和风险评分
            confidence = analysis.get("confidence")
            risk_score = analysis.get("risk_score")

            if confidence is not None:
                confidences.append(confidence)
            if risk_score is not None:
                risk_scores.append(risk_score)

            # 计算价格差距
            current_price = stock.get("current_price")
            target_price = analysis.get("target_price")
            if current_price and target_price and current_price > 0:
                gap_pct = ((target_price - current_price) / current_price) * 100
                price_gaps.append({
                    "stock_code": stock.get("stock_code"),
                    "stock_name": stock.get("stock_name"),
                    "current_price": current_price,
                    "target_price": target_price,
                    "gap_pct": gap_pct,
                    "weight": weight,
                    "confidence": confidence
                })

        total_stocks = len(stocks)
        total_weight = sum(stock.get("weight", 0) for stock in stocks)

        # 高置信度低风险股票
        high_confidence_low_risk = []
        for stock in stocks:
            analysis = stock.get("analysis_summary", {})
            confidence = analysis.get("confidence", 0)
            risk_score = analysis.get("risk_score", 1)

            if confidence > 0.7 and risk_score < 0.4:
                high_confidence_low_risk.append(self._create_stock_summary(stock))

        return {
            "action_distribution": {
                "count": {k: v for k, v in action_count.items() if v > 0},
                "weight": {k: v for k, v in total_weight_by_action.items() if v > 0},
                "percentage_by_count": {k: (v/total_stocks*100) for k, v in action_count.items() if v > 0},
                "percentage_by_weight": {k: (v/total_weight*100) for k, v in total_weight_by_action.items() if v > 0}
            },
            "confidence_stats": {
                "avg_confidence": sum(confidences)/len(confidences) if confidences else 0,
                "min_confidence": min(confidences) if confidences else 0,
                "max_confidence": max(confidences) if confidences else 0
            },
            "risk_stats": {
                "avg_risk_score": sum(risk_scores)/len(risk_scores) if risk_scores else 0,
                "min_risk_score": min(risk_scores) if risk_scores else 0,
                "max_risk_score": max(risk_scores) if risk_scores else 0
            },
            "price_gap_analysis": {
                "avg_upside_potential": sum(gap["gap_pct"] for gap in price_gaps)/len(price_gaps) if price_gaps else 0,
                "max_upside_potential": max(gap["gap_pct"] for gap in price_gaps) if price_gaps else 0,
                "high_potential_stocks": sorted(price_gaps, key=lambda x: x["gap_pct"], reverse=True)[:5]
            },
            "high_confidence_low_risk_stocks": high_confidence_low_risk[:5]
        }

    def _analyze_industry_distribution(self, stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析行业分布

        Args:
            stocks: 股票列表

        Returns:
            行业分布分析结果
        """
        industry_stats = {}

        for stock in stocks:
            industry = stock.get("industry", "未知行业")
            weight = stock.get("weight", 0)

            if industry not in industry_stats:
                industry_stats[industry] = {
                    "count": 0,
                    "total_weight": 0,
                    "stocks": []
                }

            industry_stats[industry]["count"] += 1
            industry_stats[industry]["total_weight"] += weight
            industry_stats[industry]["stocks"].append({
                "stock_code": stock.get("stock_code"),
                "stock_name": stock.get("stock_name"),
                "weight": weight,
                "action": stock.get("analysis_summary", {}).get("action", "持有")
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

        # 获取前3行业
        top_industries = []
        for industry, stats in sorted_industries[:3]:
            top_stocks = [s["stock_name"] for s in stats["stocks"][:3]]
            top_industries.append({
                "industry": industry,
                "weight_percentage": stats["weight_percentage"],
                "count": stats["count"],
                "representative_stocks": top_stocks
            })

        return {
            "by_weight": dict(sorted_industries),
            "by_count": dict(sorted(industry_stats.items(), key=lambda x: x[1]["count"], reverse=True)),
            "top_industries": top_industries
        }

    def _calculate_portfolio_score(self, stocks: List[Dict[str, Any]], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算组合综合评分

        Args:
            stocks: 股票列表
            analysis_results: 分析结果

        Returns:
            组合评分结果
        """
        if not stocks:
            return {"final_score": 50, "score_interpretation": "无数据"}

        # 计算个股评分并加权平均
        weighted_scores = []
        total_weight = 0

        for stock in stocks:
            score = self._calculate_stock_score(stock)
            weight = stock.get("weight", 0) / 100  # 转换为小数
            weighted_scores.append(score * weight)
            total_weight += weight

        weighted_avg_score = sum(weighted_scores) / total_weight if total_weight > 0 else 0

        # 信号调整
        signal_adjustment = 0
        heatmap_signals = analysis_results.get("heatmap_signals", {})
        overall_color = analysis_results.get("overall_color", {})

        if heatmap_signals.get("strong_buy_heavy"):
            signal_adjustment += 5
        if heatmap_signals.get("strong_sell_heavy"):
            signal_adjustment -= 3
        if overall_color.get("is_red"):
            signal_adjustment -= 10

        final_score = weighted_avg_score + signal_adjustment
        final_score = max(0, min(100, final_score))

        # 解释评分
        interpretation = self._interpret_score(final_score)

        return {
            "equal_weight_score": sum(self._calculate_stock_score(s) for s in stocks) / len(stocks),
            "weighted_avg_score": weighted_avg_score,
            "signal_adjustment": signal_adjustment,
            "final_score": final_score,
            "score_interpretation": interpretation
        }

    def _calculate_stock_score(self, stock: Dict[str, Any]) -> float:
        """
        计算个股综合评分

        Args:
            stock: 股票数据

        Returns:
            评分（0-100）
        """
        analysis = stock.get("analysis_summary", {})

        # 操作建议基础分
        action_scores = {
            "强力买入": 90,
            "买入": 75,
            "持有": 50,
            "卖出": 25,
            "强力卖出": 10
        }
        action = analysis.get("action", "持有")
        action_score = action_scores.get(action, 50)

        # 置信度调整
        confidence = analysis.get("confidence", 0.5)

        # 风险调整
        risk_score = analysis.get("risk_score", 0.5)

        # 估值调整
        pe_ratio = stock.get("pe_ratio")
        pe_score = 70 if pe_ratio and pe_ratio < 15 else 50

        # 动量调整
        change_pct = stock.get("change_pct", 0)
        momentum_score = 60 if change_pct > 0 else 40

        # 加权计算
        final_score = (
            action_score * 0.4 +
            confidence * 100 * 0.2 +
            (1 - risk_score) * 100 * 0.2 +
            pe_score * 0.1 +
            momentum_score * 0.1
        )

        return max(0, min(100, final_score))

    def _interpret_score(self, score: float) -> str:
        """
        解释评分结果

        Args:
            score: 评分

        Returns:
            解释文本
        """
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

    def _identify_top_signals(self, stocks: List[Dict[str, Any]],
                             heatmap_signals: Dict[str, Any],
                             ai_advice_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        识别顶级信号

        Args:
            stocks: 股票列表
            heatmap_signals: 热力图信号
            ai_advice_summary: AI建议摘要

        Returns:
            顶级信号列表
        """
        top_signals = []

        # 添加热力图关键信号
        for signal_type, signal_stocks in heatmap_signals.items():
            if signal_type in ["strong_buy_heavy", "strong_sell_heavy", "strong_buy_light"] and signal_stocks:
                for stock in signal_stocks[:2]:  # 每种类型取前2个
                    top_signals.append({
                        "type": signal_type,
                        "stock_code": stock.get("stock_code"),
                        "stock_name": stock.get("stock_name"),
                        "description": self._get_signal_description(signal_type, stock),
                        "priority": "high" if signal_type == "strong_buy_heavy" else "medium"
                    })

        # 添加上涨潜力大的股票
        high_potential = ai_advice_summary.get("price_gap_analysis", {}).get("high_potential_stocks", [])
        for stock_info in high_potential[:3]:
            stock_code = stock_info.get("stock_code")
            if stock_code:
                # 找到完整的股票信息
                full_stock = next((s for s in stocks if s.get("stock_code") == stock_code), None)
                if full_stock:
                    top_signals.append({
                        "type": "high_upside_potential",
                        "stock_code": stock_code,
                        "stock_name": stock_info.get("stock_name"),
                        "description": f"目标价上涨空间{stock_info.get('gap_pct', 0):.1f}%",
                        "priority": "medium"
                    })

        return top_signals

    def _generate_recommendations(self, stocks: List[Dict[str, Any]],
                                 heatmap_signals: Dict[str, Any],
                                 overall_color: Dict[str, Any],
                                 portfolio_score: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成投资建议

        Args:
            stocks: 股票列表
            heatmap_signals: 热力图信号
            overall_color: 整体颜色分析
            portfolio_score: 组合评分

        Returns:
            投资建议
        """
        immediate_actions = []
        watch_list = []
        risk_warnings = []

        # 基于热力图信号生成建议
        strong_buy_heavy = heatmap_signals.get("strong_buy_heavy", [])
        if strong_buy_heavy:
            stock_names = [s.get("stock_name") for s in strong_buy_heavy[:3]]
            immediate_actions.append(f"重点分析'{', '.join(stock_names)}'，关注其重仓且AI看好的逻辑")

            for stock in strong_buy_heavy[:2]:
                watch_list.append({
                    "stock_code": stock.get("stock_code"),
                    "stock_name": stock.get("stock_name"),
                    "reason": "重仓+AI看好双重信号",
                    "monitoring_points": ["季度财报业绩", "行业政策变化", "技术面突破"]
                })

        strong_sell_heavy = heatmap_signals.get("strong_sell_heavy", [])
        if strong_sell_heavy:
            stock_names = [s.get("stock_name") for s in strong_sell_heavy[:2]]
            immediate_actions.append(f"深入研究'{', '.join(stock_names)}'的分歧点，分析大师重仓与AI看空的矛盾")

        # 基于整体颜色生成风险提示
        if overall_color.get("is_red"):
            red_percentage = overall_color.get("red_percentage", 0)
            risk_warnings.append(f"整体持仓偏红，{red_percentage:.1f}%的股票被AI看空，入场需谨慎")

        # 基于评分生成建议
        final_score = portfolio_score.get("final_score", 50)
        if final_score < 60:
            risk_warnings.append("组合综合评分较低，建议控制仓位或等待更好时机")

        avg_confidence = next(iter(stocks), {}).get("analysis_summary", {}).get("confidence", 0) if stocks else 0
        if avg_confidence < 0.6:
            risk_warnings.append("AI建议平均置信度较低，建议结合其他分析方法")

        return {
            "immediate_actions": immediate_actions,
            "watch_list": watch_list[:5],
            "risk_warnings": risk_warnings
        }

    def _create_stock_summary(self, stock: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建股票摘要

        Args:
            stock: 完整股票数据

        Returns:
            股票摘要
        """
        analysis = stock.get("analysis_summary", {})

        # 计算上涨潜力
        current_price = stock.get("current_price")
        target_price = analysis.get("target_price")
        upside_potential = 0
        if current_price and target_price and current_price > 0:
            upside_potential = ((target_price - current_price) / current_price) * 100

        return {
            "stock_code": stock.get("stock_code"),
            "stock_name": stock.get("stock_name"),
            "weight": stock.get("weight"),
            "ai_rating": self._map_action_to_rating(analysis.get("action")),
            "ai_score": self._calculate_stock_score(stock),
            "current_price": current_price,
            "change_pct": stock.get("change_pct"),
            "pe_ratio": stock.get("pe_ratio"),
            "pb_ratio": stock.get("pb_ratio"),
            "action": analysis.get("action"),
            "confidence": analysis.get("confidence"),
            "target_price": target_price,
            "upside_potential": upside_potential
        }

    def _map_action_to_rating(self, action: str) -> str:
        """
        将action映射到AI评级

        Args:
            action: 操作建议

        Returns:
            AI评级
        """
        mapping = {
            "强力买入": "Strong Buy",
            "买入": "Buy",
            "持有": "Hold",
            "卖出": "Sell",
            "强力卖出": "Strong Sell"
        }
        return mapping.get(action, "Hold")

    def _get_signal_description(self, signal_type: str, stock: Dict[str, Any]) -> str:
        """
        获取信号描述

        Args:
            signal_type: 信号类型
            stock: 股票摘要

        Returns:
            信号描述
        """
        descriptions = {
            "strong_buy_heavy": f"重仓且AI看好，权重{stock.get('weight')}%，AI评级'{stock.get('ai_rating')}'",
            "strong_sell_heavy": f"重仓但AI看空，权重{stock.get('weight')}%，AI评级'{stock.get('ai_rating')}'",
            "strong_buy_light": f"轻仓但AI看好，权重{stock.get('weight')}%，AI评级'{stock.get('ai_rating')}'",
            "high_upside_potential": f"目标价上涨空间{stock.get('upside_potential', 0):.1f}%"
        }
        return descriptions.get(signal_type, "")

    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """
        计算统计值

        Args:
            values: 数值列表

        Returns:
            统计结果
        """
        if not values:
            return {}

        sorted_vals = sorted(values)
        n = len(values)

        return {
            "min": min(values),
            "p25": sorted_vals[n // 4] if n >= 4 else sorted_vals[0],
            "median": sorted_vals[n // 2] if n >= 2 else sorted_vals[0],
            "p75": sorted_vals[3 * n // 4] if n >= 4 else sorted_vals[-1],
            "max": max(values),
            "avg": sum(values) / n,
            "count": n
        }

    def generate_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        生成自然语言总结

        Args:
            analysis_results: 分析结果

        Returns:
            自然语言总结
        """
        metadata = analysis_results.get("metadata", {})
        heatmap_signals = analysis_results.get("heatmap_signals", {})
        overall_color = analysis_results.get("overall_color", {})
        financial = analysis_results.get("financial_analysis", {})
        ai_advice = analysis_results.get("ai_advice_summary", {})
        industry = analysis_results.get("industry_distribution", {})
        portfolio_score = analysis_results.get("portfolio_score", {})
        recommendations = analysis_results.get("recommendations", {})

        # 构建总结
        summary_parts = []

        # 1. 持仓概况
        total_stocks = metadata.get("total_stocks", 0)
        fund_code = metadata.get("fund_code", "unknown")
        summary_parts.append(f"【基金持仓分析报告 - {fund_code}】\n")

        overview = f"本次分析涵盖{total_stocks}只持仓股票。"
        summary_parts.append(f"一、持仓概况\n{overview}\n")

        # 2. 关键信号发现
        signals_text = []
        strong_buy_heavy = heatmap_signals.get("strong_buy_heavy", [])
        strong_sell_heavy = heatmap_signals.get("strong_sell_heavy", [])
        strong_buy_light = heatmap_signals.get("strong_buy_light", [])

        if strong_buy_heavy:
            count = len(strong_buy_heavy)
            names = [s.get("stock_name") for s in strong_buy_heavy[:3]]
            signals_text.append(f"发现{count}只'重仓且AI看好'股票，包括{', '.join(names)}等")

        if strong_sell_heavy:
            count = len(strong_sell_heavy)
            names = [s.get("stock_name") for s in strong_sell_heavy[:2]]
            signals_text.append(f"发现{count}只'重仓但AI看空'股票，包括{', '.join(names)}，存在明显分歧")

        if strong_buy_light:
            count = len(strong_buy_light)
            names = [s.get("stock_name") for s in strong_buy_light[:2]]
            signals_text.append(f"发现{count}只'轻仓但AI看好'股票，包括{', '.join(names)}，值得关注")

        if overall_color.get("is_red"):
            red_percentage = overall_color.get("red_percentage", 0)
            signals_text.append(f"整体持仓偏红，{red_percentage:.1f}%的股票被AI看空，需谨慎对待")

        signals_summary = "；".join(signals_text) if signals_text else "未发现显著关键信号。"
        summary_parts.append(f"二、关键信号发现\n{signals_summary}\n")

        # 3. 财务指标分析
        financial_text = []
        valuation = financial.get("valuation_summary", {})
        momentum = financial.get("momentum_summary", {})
        liquidity = financial.get("liquidity_summary", {})

        pe_stats = valuation.get("pe_stats", {})
        if pe_stats:
            avg_pe = pe_stats.get("avg", 0)
            financial_text.append(f"估值水平：平均PE {avg_pe:.1f}倍")

        avg_change = momentum.get("avg_change", 0)
        financial_text.append(f"价格动量：平均涨幅{avg_change:.1f}%")

        avg_turnover = liquidity.get("avg_turnover", 0)
        financial_text.append(f"流动性：平均换手率{avg_turnover:.1f}%")

        financial_summary = "；".join(financial_text) if financial_text else "财务数据不完整。"
        summary_parts.append(f"三、财务指标分析\n{financial_summary}\n")

        # 4. AI投资建议汇总
        ai_text = []
        action_dist = ai_advice.get("action_distribution", {})
        confidence_stats = ai_advice.get("confidence_stats", {})
        price_gap = ai_advice.get("price_gap_analysis", {})

        # 操作建议分布
        count_dist = action_dist.get("percentage_by_count", {})
        if count_dist:
            main_action = max(count_dist.items(), key=lambda x: x[1])
            ai_text.append(f"操作建议：{main_action[0]}占比{main_action[1]:.1f}%")

        avg_confidence = confidence_stats.get("avg_confidence", 0)
        ai_text.append(f"平均置信度：{avg_confidence:.2f}")

        avg_upside = price_gap.get("avg_upside_potential", 0)
        ai_text.append(f"目标价空间：平均上涨潜力{avg_upside:.1f}%")

        ai_summary = "；".join(ai_text) if ai_text else "AI建议数据不完整。"
        summary_parts.append(f"四、AI投资建议汇总\n{ai_summary}\n")

        # 5. 行业分布特征
        industry_text = []
        top_industries = industry.get("top_industries", [])
        if top_industries:
            for i, ind in enumerate(top_industries[:3]):
                industry_text.append(f"{ind['industry']}（{ind['weight_percentage']:.1f}%）")
            industry_summary = f"持仓集中在{len(top_industries)}个行业：{', '.join(industry_text)}"
        else:
            industry_summary = "行业分布数据不完整。"

        summary_parts.append(f"五、行业分布特征\n{industry_summary}\n")

        # 6. 综合评估
        final_score = portfolio_score.get("final_score", 0)
        interpretation = portfolio_score.get("score_interpretation", "")
        assessment = f"组合综合评分：{final_score:.1f}/100（{interpretation}）"
        summary_parts.append(f"六、综合评估\n{assessment}\n")

        # 7. 投资建议
        recommendations_text = []
        immediate_actions = recommendations.get("immediate_actions", [])
        risk_warnings = recommendations.get("risk_warnings", [])

        if immediate_actions:
            recommendations_text.append(f"重点关注：{immediate_actions[0]}")

        if risk_warnings:
            recommendations_text.append(f"风险提示：{risk_warnings[0]}")

        recommendations_summary = "；".join(recommendations_text) if recommendations_text else "无特别建议。"
        summary_parts.append(f"七、投资建议\n{recommendations_summary}\n")

        # 8. 报告信息
        summary_parts.append(f"报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_parts.append("数据来源：ai2alpha.cn")

        return "\n".join(summary_parts)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='分析基金持仓数据')
    parser.add_argument('--input', '-i', required=True, help='输入JSON文件路径')
    parser.add_argument('--output', '-o', help='结构化报告输出路径')
    parser.add_argument('--summary-text', '-s', help='自然语言总结输出路径')
    parser.add_argument('--verbose', action='store_true', help='输出详细信息')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # 初始化分析器
        analyzer = FundHeatmapAnalyzer()

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

        # 控制台输出
        if not args.output and not args.summary_text:
            print(summary)

        # 输出关键信息
        fund_code = analysis_results.get("metadata", {}).get("fund_code", "unknown")
        total_stocks = analysis_results.get("metadata", {}).get("total_stocks", 0)
        final_score = analysis_results.get("portfolio_score", {}).get("final_score", 0)

        print(f"\n分析完成!")
        print(f"基金代码: {fund_code}")
        print(f"分析股票: {total_stocks} 只")
        print(f"综合评分: {final_score:.1f}/100")

        # 显示关键信号
        heatmap_signals = analysis_results.get("heatmap_signals", {})
        for signal_type, signals in heatmap_signals.items():
            if signals and signal_type in ["strong_buy_heavy", "strong_sell_heavy"]:
                print(f"\n{signal_type}: {len(signals)} 个")

        return 0

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
