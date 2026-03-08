#!/usr/bin/env python3
"""
基金个股持仓双轴历史图分析器 - 核心模块

功能：提供基金持仓数据分析的核心功能，包括：
1. 数据加载和验证
2. 个股精选算法
3. 双轴图数据分析
4. 收益分析和操作节点识别
5. 报告生成

使用示例：
    from scripts.analyzer import FundDualAxisAnalyzer

    # 初始化分析器
    analyzer = FundDualAxisAnalyzer()

    # 分析数据
    data = {...}  # API返回的JSON数据
    report = analyzer.analyze(data)

    # 获取结构化报告
    json_report = report.to_json()

    # 获取CSV数据
    csv_data = report.generate_csv_data()

    # 获取自然语言总结
    text_summary = report.generate_summary()
"""

import json
import csv
import os
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import statistics
import numpy as np
from dataclasses import dataclass, field, asdict
from enum import Enum

class ProfitType(Enum):
    """收益类型枚举"""
    POSITIVE = "positive_profit"
    NEGATIVE = "negative_profit"
    NEUTRAL = "neutral"

class TrendType(Enum):
    """趋势类型枚举"""
    UPTREND = "uptrend"
    SLIGHT_UPTREND = "slight_uptrend"
    DOWNTREND = "downtrend"
    SLIGHT_DOWNTREND = "slight_downtrend"
    STABLE = "stable"
    MIXED = "mixed"

@dataclass
class StockPosition:
    """股票持仓数据类"""
    stock_code: str
    stock_name: str
    shares: float
    market_value: float
    weight: float
    quarter: str
    as_of_date: str

@dataclass
class StockTimeSeries:
    """股票时间序列数据类"""
    stock_code: str
    stock_name: str
    quarters: List[str] = field(default_factory=list)
    market_values: List[float] = field(default_factory=list)
    shares: List[float] = field(default_factory=list)
    weights: List[float] = field(default_factory=list)
    quarter_dates: List[str] = field(default_factory=list)

    def add_position(self, position: StockPosition):
        """添加持仓数据"""
        self.quarters.append(position.quarter)
        self.market_values.append(position.market_value)
        self.shares.append(position.shares)
        self.weights.append(position.weight)
        self.quarter_dates.append(position.as_of_date)

    def get_avg_weight(self) -> float:
        """计算平均权重"""
        if not self.weights:
            return 0.0
        return statistics.mean(self.weights)

    def get_quarters_held_ratio(self, total_quarters: int) -> float:
        """计算持仓季度比例"""
        if total_quarters == 0:
            return 0.0
        return len(self.quarters) / total_quarters

@dataclass
class SlopeAnalysis:
    """斜率分析结果"""
    market_value_slope: float = 0.0
    shares_slope: float = 0.0
    profit_differential: float = 0.0
    calculation_method: str = "linear_regression"
    r_squared: Optional[float] = None
    confidence: Optional[float] = None

@dataclass
class ProfitAnalysis:
    """收益分析结果"""
    profit_type: ProfitType = ProfitType.NEUTRAL
    profit_strength: str = "neutral"
    profit_differential_percentage: float = 0.0
    price_contribution: float = 0.0
    shares_contribution: float = 0.0
    estimated_annual_return: Optional[float] = None
    risk_adjusted_return: Optional[float] = None

@dataclass
class OperationNode:
    """操作节点"""
    stock_code: str
    stock_name: str
    quarter: str
    previous_shares: float
    current_shares: float
    change_pct: float
    node_type: str  # 'increase' or 'decrease'
    significance_level: str  # 'high', 'medium', 'low'
    market_value_before: Optional[float] = None
    market_value_after: Optional[float] = None
    context: Optional[str] = None

@dataclass
class StockSelectionResult:
    """个股精选结果"""
    stock_code: str
    stock_name: str
    avg_weight: float
    quarters_held: int
    quarters_held_ratio: float
    weight_slope: float
    market_value_slope: float
    shares_slope: float
    scores: Dict[str, float]
    comprehensive_score: float
    selection_reason: Optional[str] = None

@dataclass
class AnalysisReport:
    """分析报告"""
    metadata: Dict[str, Any]
    key_stocks_selection: Dict[str, Any]
    dual_axis_analysis: Dict[str, Any]
    operation_nodes: Dict[str, Any]
    industry_analysis: Dict[str, Any]
    blog_content_support: Dict[str, Any]
    recommendations: Dict[str, Any]
    performance_metrics: Dict[str, Any]

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(asdict(self), ensure_ascii=False, indent=indent)

    def save(self, filepath: str):
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    def generate_csv_data(self, output_dir: str, market_value_unit: float = 100000000,
                         shares_unit: float = 1000000):
        """生成CSV数据"""
        os.makedirs(output_dir, exist_ok=True)

        # 从dual_axis_analysis中获取股票数据
        # 注意：这里需要原始数据，简化实现
        pass

    def generate_summary(self, language: str = "zh-CN") -> str:
        """生成自然语言总结"""
        # 简化实现
        fund_code = self.metadata.get('fund_code', '未知')
        fund_name = self.metadata.get('fund_name', '未知')

        summary = f"# {fund_name}({fund_code})持仓分析报告\n\n"
        summary += f"分析日期: {self.metadata.get('analysis_date', '未知')}\n"
        summary += f"分析季度数: {self.metadata.get('total_quarters', 0)}\n\n"

        # 添加关键个股信息
        selected_stocks = self.key_stocks_selection.get('selected_stocks', [])
        if selected_stocks:
            summary += "## 关键个股\n"
            for stock in selected_stocks[:3]:  # 显示前3个
                summary += f"- {stock['stock_name']}({stock['stock_code']}): 评分{stock['final_score']}\n"

        return summary

class FundDualAxisAnalyzer:
    """基金双轴图分析器（核心类）"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化分析器"""
        self.config = config or self._get_default_config()
        self.data = None
        self.stock_time_series = {}
        self.analysis_report = None

    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'stock_selection_thresholds': {
                'min_avg_weight': 3.0,
                'min_quarters_held': 0.7,
                'min_slope_positive': 0.01,
                'max_stocks_to_select': 5,
                'selection_weights': {
                    'avg_weight': 0.3,
                    'holding_stability': 0.25,
                    'weight_trend': 0.2,
                    'profit_performance': 0.15,
                    'industry_representation': 0.1
                }
            },
            'dual_axis_analysis': {
                'market_value_unit': 100000000,  # 1亿
                'shares_unit': 1000000,  # 1百万股
                'significant_change_threshold': 0.2,  # 20%
                'min_quarters_for_trend': 4,
                'slope_calculation_method': 'linear_regression'
            },
            'profit_analysis': {
                'positive_profit_threshold': 0.05,
                'high_profit_threshold': 0.15,
                'loss_threshold': -0.05,
                'significant_loss_threshold': -0.1
            }
        }

    def load_data(self, data: Dict[str, Any]) -> None:
        """加载数据"""
        self._validate_data(data)
        self.data = data
        self._organize_stock_time_series()

    def _validate_data(self, data: Dict[str, Any]) -> None:
        """验证数据格式"""
        required_fields = ['master_code', 'items']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"数据缺少必需字段: {field}")

        if not isinstance(data['items'], list):
            raise ValueError("items字段必须是列表")

        if len(data['items']) == 0:
            raise ValueError("数据中没有季度持仓数据")

    def _organize_stock_time_series(self) -> None:
        """组织股票时间序列数据"""
        self.stock_time_series = {}

        # 按时间排序
        sorted_items = sorted(self.data['items'],
                            key=lambda x: x['as_of_date'])

        for item in sorted_items:
            quarter = self._date_to_quarter(item['as_of_date'])

            for position_data in item.get('a_positions', []):
                position = StockPosition(
                    stock_code=position_data['stock_code'],
                    stock_name=position_data['stock_name'],
                    shares=position_data['shares'],
                    market_value=position_data['market_value'],
                    weight=position_data['weight'],
                    quarter=quarter,
                    as_of_date=item['as_of_date']
                )

                stock_code = position.stock_code
                if stock_code not in self.stock_time_series:
                    self.stock_time_series[stock_code] = StockTimeSeries(
                        stock_code=stock_code,
                        stock_name=position.stock_name
                    )

                self.stock_time_series[stock_code].add_position(position)

    @staticmethod
    def _date_to_quarter(date_str: str) -> str:
        """将日期转换为季度格式"""
        try:
            year = date_str[:4]
            month = int(date_str[5:7])
            quarter = (month - 1) // 3 + 1
            return f"{year}Q{quarter}"
        except:
            return date_str

    def analyze(self) -> AnalysisReport:
        """执行完整分析"""
        if self.data is None:
            raise ValueError("请先加载数据")

        # 1. 个股精选
        key_stocks = self._select_key_stocks()

        # 2. 双轴图数据分析
        dual_axis_analysis = self._analyze_dual_axis_data(key_stocks)

        # 3. 操作节点识别
        operation_nodes = self._identify_operation_nodes(key_stocks)

        # 4. 行业分析
        industry_analysis = self._analyze_industry_distribution()

        # 5. 生成报告
        report = self._generate_report(
            key_stocks,
            dual_axis_analysis,
            operation_nodes,
            industry_analysis
        )

        self.analysis_report = report
        return report

    def _select_key_stocks(self) -> List[StockSelectionResult]:
        """精选关键个股"""
        candidate_stocks = []
        total_quarters = len(self.data['items'])

        for stock_code, ts_data in self.stock_time_series.items():
            if len(ts_data.quarters) < 2:
                continue  # 至少需要2个季度数据

            # 计算各项指标
            avg_weight = ts_data.get_avg_weight()
            quarters_held = len(ts_data.quarters)
            quarters_held_ratio = ts_data.get_quarters_held_ratio(total_quarters)

            # 计算斜率
            weight_slope = self._calculate_slope(ts_data.weights)
            market_value_slope = self._calculate_slope(ts_data.market_values)
            shares_slope = self._calculate_slope(ts_data.shares)

            # 计算各项得分
            scores = {
                'avg_weight_score': self._calculate_weight_score(avg_weight),
                'holding_stability_score': self._calculate_stability_score(quarters_held_ratio),
                'weight_trend_score': self._calculate_trend_score(weight_slope),
                'profit_performance_score': self._calculate_profit_score(market_value_slope, shares_slope),
                'industry_representation_score': self._calculate_industry_score(stock_code, ts_data.stock_name)
            }

            # 计算综合评分
            weights = self.config['stock_selection_thresholds']['selection_weights']
            comprehensive_score = self._calculate_comprehensive_score(scores, weights)

            candidate_stocks.append(StockSelectionResult(
                stock_code=stock_code,
                stock_name=ts_data.stock_name,
                avg_weight=avg_weight,
                quarters_held=quarters_held,
                quarters_held_ratio=quarters_held_ratio,
                weight_slope=weight_slope,
                market_value_slope=market_value_slope,
                shares_slope=shares_slope,
                scores=scores,
                comprehensive_score=comprehensive_score
            ))

        # 按综合评分排序
        candidate_stocks.sort(key=lambda x: x.comprehensive_score, reverse=True)

        # 应用筛选条件
        min_avg_weight = self.config['stock_selection_thresholds']['min_avg_weight']
        min_quarters_held = self.config['stock_selection_thresholds']['min_quarters_held']
        max_stocks = self.config['stock_selection_thresholds']['max_stocks_to_select']

        selected_stocks = []
        for stock in candidate_stocks:
            if (stock.avg_weight >= min_avg_weight and
                stock.quarters_held_ratio >= min_quarters_held):
                selected_stocks.append(stock)
                if len(selected_stocks) >= max_stocks:
                    break

        return selected_stocks

    def _calculate_slope(self, values: List[float]) -> float:
        """计算斜率"""
        if len(values) < 2:
            return 0.0

        method = self.config['dual_axis_analysis']['slope_calculation_method']

        if method == 'simple_slope':
            # 简单首尾斜率
            return (values[-1] - values[0]) / (len(values) - 1)
        else:
            # 线性回归
            x = np.arange(len(values))
            y = np.array(values)

            x_mean = np.mean(x)
            y_mean = np.mean(y)

            numerator = np.sum((x - x_mean) * (y - y_mean))
            denominator = np.sum((x - x_mean) ** 2)

            if denominator == 0:
                return 0.0

            return numerator / denominator

    def _calculate_weight_score(self, avg_weight: float) -> float:
        """计算持仓权重得分"""
        min_threshold = 3.0
        max_threshold = 20.0

        if avg_weight < min_threshold:
            return 0.0
        elif avg_weight > max_threshold:
            return 100.0
        else:
            return ((avg_weight - min_threshold) / (max_threshold - min_threshold)) * 100.0

    def _calculate_stability_score(self, quarters_held_ratio: float) -> float:
        """计算持仓稳定性得分"""
        min_ratio = self.config['stock_selection_thresholds']['min_quarters_held']

        if quarters_held_ratio < min_ratio:
            return 0.0
        else:
            return ((quarters_held_ratio - min_ratio) / (1.0 - min_ratio)) * 100.0

    def _calculate_trend_score(self, slope: float) -> float:
        """计算趋势得分"""
        min_slope = self.config['stock_selection_thresholds']['min_slope_positive']

        if slope > min_slope:
            return min(100.0, (slope / (min_slope * 5)) * 100.0)
        elif slope < -min_slope:
            return max(-100.0, (slope / (min_slope * 5)) * 100.0)
        else:
            return 0.0

    def _calculate_profit_score(self, market_value_slope: float, shares_slope: float) -> float:
        """计算收益表现得分"""
        profit_differential = market_value_slope - shares_slope

        if profit_differential > 0:
            return min(100.0, profit_differential * 1000.0)
        else:
            return max(-100.0, profit_differential * 1000.0)

    def _calculate_industry_score(self, stock_code: str, stock_name: str) -> float:
        """计算行业代表性得分（简化版本）"""
        # 在实际应用中，这里应该根据行业分类和排名计算得分
        return 50.0

    def _calculate_comprehensive_score(self, scores: Dict[str, float],
                                     weights: Dict[str, float]) -> float:
        """计算综合评分"""
        total_score = 0.0
        total_weight = 0.0

        for dimension, score in scores.items():
            if dimension in weights:
                weight = weights[dimension]

                # 归一化：将-100到100的得分映射到0-100
                if score < 0:
                    normalized_score = 50.0 + (score / 2.0)
                else:
                    normalized_score = 50.0 + (score / 2.0)

                total_score += normalized_score * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _analyze_dual_axis_data(self, key_stocks: List[StockSelectionResult]) -> Dict[str, Any]:
        """分析双轴图数据"""
        analysis_results = {
            'csv_data_samples': {},
            'slope_analysis': {},
            'profit_analysis': {},
            'trend_analysis': {}
        }

        for stock in key_stocks:
            stock_code = stock.stock_code
            ts_data = self.stock_time_series[stock_code]

            # 斜率分析
            slope_analysis = self._analyze_slopes(ts_data)

            # 收益分析
            profit_analysis = self._analyze_profit(slope_analysis)

            # 趋势分析
            trend_analysis = self._analyze_trends(ts_data)

            # CSV数据样本
            csv_sample = self._generate_csv_sample(stock_code, ts_data)

            analysis_results['csv_data_samples'][stock_code] = csv_sample
            analysis_results['slope_analysis'][stock_code] = asdict(slope_analysis)
            analysis_results['profit_analysis'][stock_code] = asdict(profit_analysis)
            analysis_results['trend_analysis'][stock_code] = trend_analysis

        return analysis_results

    def _analyze_slopes(self, ts_data: StockTimeSeries) -> SlopeAnalysis:
        """分析斜率"""
        market_value_slope = self._calculate_slope(ts_data.market_values)
        shares_slope = self._calculate_slope(ts_data.shares)
        profit_differential = market_value_slope - shares_slope

        return SlopeAnalysis(
            market_value_slope=market_value_slope,
            shares_slope=shares_slope,
            profit_differential=profit_differential,
            calculation_method=self.config['dual_axis_analysis']['slope_calculation_method']
        )

    def _analyze_profit(self, slope_analysis: SlopeAnalysis) -> ProfitAnalysis:
        """分析收益"""
        profit_differential = slope_analysis.profit_differential

        # 判断收益类型
        threshold = self.config['stock_selection_thresholds']['min_slope_positive']
        if profit_differential > threshold:
            profit_type = ProfitType.POSITIVE
        elif profit_differential < -threshold:
            profit_type = ProfitType.NEGATIVE
        else:
            profit_type = ProfitType.NEUTRAL

        # 判断收益强度
        profit_config = self.config['profit_analysis']
        if profit_differential > profit_config['high_profit_threshold']:
            profit_strength = 'high_positive'
        elif profit_differential > profit_config['positive_profit_threshold']:
            profit_strength = 'moderate_positive'
        elif profit_differential > 0.01:
            profit_strength = 'low_positive'
        elif profit_differential > -0.01:
            profit_strength = 'neutral'
        elif profit_differential > profit_config['loss_threshold']:
            profit_strength = 'low_negative'
        elif profit_differential > profit_config['significant_loss_threshold']:
            profit_strength = 'moderate_negative'
        else:
            profit_strength = 'high_negative'

        return ProfitAnalysis(
            profit_type=profit_type,
            profit_strength=profit_strength,
            profit_differential_percentage=profit_differential * 100
        )

    def _analyze_trends(self, ts_data: StockTimeSeries) -> Dict[str, str]:
        """分析趋势"""
        market_value_trend = self._detect_trend(ts_data.market_values)
        shares_trend = self._detect_trend(ts_data.shares)

        # 判断组合趋势
        if market_value_trend == TrendType.UPTREND and shares_trend in [TrendType.UPTREND, TrendType.SLIGHT_UPTREND, TrendType.STABLE]:
            combined_trend = 'positive_profit_trend'
        elif market_value_trend == TrendType.DOWNTREND and shares_trend in [TrendType.DOWNTREND, TrendType.SLIGHT_DOWNTREND]:
            combined_trend = 'negative_profit_trend'
        else:
            combined_trend = 'mixed_trend'

        return {
            'market_value_trend': market_value_trend.value,
            'shares_trend': shares_trend.value,
            'combined_trend': combined_trend
        }

    def _detect_trend(self, values: List[float]) -> TrendType:
        """检测趋势"""
        if len(values) < 2:
            return TrendType.STABLE

        slope = self._calculate_slope(values)

        if slope > 0.1:
            return TrendType.UPTREND
        elif slope > 0.05:
            return TrendType.SLIGHT_UPTREND
        elif slope < -0.1:
            return TrendType.DOWNTREND
        elif slope < -0.05:
            return TrendType.SLIGHT_DOWNTREND
        else:
            return TrendType.STABLE

    def _generate_csv_sample(self, stock_code: str, ts_data: StockTimeSeries) -> Dict[str, Any]:
        """生成CSV数据样本"""
        market_value_unit = self.config['dual_axis_analysis']['market_value_unit']
        shares_unit = self.config['dual_axis_analysis']['shares_unit']

        sample_rows = []
        for i in range(min(3, len(ts_data.quarters))):  # 取前3行作为样本
            market_value_100m = ts_data.market_values[i] / market_value_unit
            shares_million = ts_data.shares[i] / shares_unit

            sample_rows.append([
                ts_data.quarters[i],
                stock_code,
                round(market_value_100m, 2),
                round(shares_million, 2)
            ])

        return {
            'header': ['quarter', 'ticker', 'market_value_100m', 'shares_million'],
            'sample_rows': sample_rows,
            'total_rows': len(ts_data.quarters)
        }

    def _identify_operation_nodes(self, key_stocks: List[StockSelectionResult]) -> Dict[str, List[OperationNode]]:
        """识别操作节点"""
        operation_nodes = {
            'significant_increases': [],
            'significant_decreases': []
        }

        threshold = self.config['dual_axis_analysis']['significant_change_threshold']

        for stock in key_stocks:
            stock_code = stock.stock_code
            ts_data = self.stock_time_series[stock_code]

            if len(ts_data.shares) < 2:
                continue

            # 检测大幅变化
            for i in range(1, len(ts_data.shares)):
                current = ts_data.shares[i]
                previous = ts_data.shares[i-1]

                if previous == 0:
                    continue

                change_pct = (current - previous) / abs(previous)

                if abs(change_pct) >= threshold:
                    node_type = 'increase' if change_pct > 0 else 'decrease'
                    significance = 'high' if abs(change_pct) >= 0.3 else 'medium'

                    node = OperationNode(
                        stock_code=stock_code,
                        stock_name=ts_data.stock_name,
                        quarter=ts_data.quarters[i],
                        previous_shares=previous,
                        current_shares=current,
                        change_pct=change_pct * 100,
                        node_type=node_type,
                        significance_level=significance,
                        market_value_before=ts_data.market_values[i-1] if i-1 < len(ts_data.market_values) else None,
                        market_value_after=ts_data.market_values[i] if i < len(ts_data.market_values) else None
                    )

                    if node_type == 'increase':
                        operation_nodes['significant_increases'].append(node)
                    else:
                        operation_nodes['significant_decreases'].append(node)

        return operation_nodes

    def _analyze_industry_distribution(self) -> Dict[str, Any]:
        """分析行业分布（简化版本）"""
        # 在实际应用中，这里应该根据行业分类进行详细分析
        return {
            'industry_distribution': [],
            'concentration_analysis': {
                'top_3_industries_weight': 0.0,
                'concentration_level': 'unknown'
            }
        }

    def _generate_report(self, key_stocks: List[StockSelectionResult],
                        dual_axis_analysis: Dict[str, Any],
                        operation_nodes: Dict[str, List[OperationNode]],
                        industry_analysis: Dict[str, Any]) -> AnalysisReport:
        """生成分析报告"""
        fund_code = self.data['master_code']
        fund_name = self.data['items'][0]['master_name'] if self.data['items'] else '未知'

        # 转换操作节点为字典
        operation_nodes_dict = {
            'significant_increases': [asdict(node) for node in operation_nodes['significant_increases']],
            'significant_decreases': [asdict(node) for node in operation_nodes['significant_decreases']]
        }

        # 准备精选个股数据
        candidate_stocks_dict = [asdict(stock) for stock in key_stocks]
        selected_stocks = [
            {
                'rank': i + 1,
                'stock_code': stock.stock_code,
                'stock_name': stock.stock_name,
                'final_score': round(stock.comprehensive_score, 1),
                'selection_priority': 'high' if stock.comprehensive_score > 80 else 'medium'
            }
            for i, stock in enumerate(key_stocks)
        ]

        # 生成报告
        report = AnalysisReport(
            metadata={
                'fund_code': fund_code,
                'fund_name': fund_name,
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'total_quarters': len(self.data['items']),
                'quarters_analyzed': len(self.data['items']),
                'total_stocks': len(self.stock_time_series),
                'analysis_version': '1.0.0',
                'analysis_timestamp': datetime.now().isoformat()
            },
            key_stocks_selection={
                'selection_criteria': self.config['stock_selection_thresholds'],
                'candidate_stocks': candidate_stocks_dict,
                'selected_stocks': selected_stocks
            },
            dual_axis_analysis=dual_axis_analysis,
            operation_nodes=operation_nodes_dict,
            industry_analysis=industry_analysis,
            blog_content_support={
                'visualization_suggestions': [],
                'key_insights': [],
                'content_outline': {}
            },
            recommendations={
                'focus_stocks': [
                    {
                        'stock_code': key_stocks[0].stock_code,
                        'stock_name': key_stocks[0].stock_name,
                        'recommendation_reason': '综合评分最高',
                        'analysis_priority': 'highest'
                    }
                ] if key_stocks else [],
                'analysis_priorities': [
                    {
                        'priority': 1,
                        'task': '深度分析收益表现最佳的个股',
                        'reason': '了解大师的成功投资逻辑'
                    }
                ]
            },
            performance_metrics={
                'stocks_analyzed': len(self.stock_time_series),
                'key_stocks_selected': len(key_stocks)
            }
        )

        return report

    def generate_csv_files(self, output_dir: str):
        """生成CSV文件"""
        os.makedirs(output_dir, exist_ok=True)

        market_value_unit = self.config['dual_axis_analysis']['market_value_unit']
        shares_unit = self.config['dual_axis_analysis']['shares_unit']

        for stock_code, ts_data in self.stock_time_series.items():
            filename = f"{stock_code}_{self.data['master_code']}_dual_axis.csv"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['quarter', 'ticker', 'market_value_100m', 'shares_million'])

                for i in range(len(ts_data.quarters)):
                    market_value_100m = ts_data.market_values[i] / market_value_unit
                    shares_million = ts_data.shares[i] / shares_unit

                    writer.writerow([
                        ts_data.quarters[i],
                        stock_code,
                        round(market_value_100m, 2),
                        round(shares_million, 2)
                    ])


# 导出主要的类
__all__ = [
    'FundDualAxisAnalyzer',
    'AnalysisReport',
    'StockSelectionResult',
    'ProfitType',
    'TrendType'
]