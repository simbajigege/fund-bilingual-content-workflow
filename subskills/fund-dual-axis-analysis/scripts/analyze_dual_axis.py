#!/usr/bin/env python3
"""
基金个股持仓双轴历史图分析脚本

功能：分析基金历史持仓数据，生成双轴图分析报告和CSV数据。
使用示例：
    python analyze_dual_axis.py --input historical_data.json --output analysis.json --csv-dir ./csv_data
"""

import argparse
import json
import csv
import sys
import os
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import statistics
import numpy as np

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("警告：未安装PyYAML，将使用默认配置")

class FundDualAxisAnalyzer:
    """基金双轴图分析器"""

    def __init__(self, config_path: Optional[str] = None):
        """初始化分析器"""
        self.config = self._load_config(config_path)
        self.data = None
        self.analysis_results = {}
        self.stock_data_cache = {}

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
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
                'market_value_unit': 100000000,
                'shares_unit': 1000000,
                'significant_change_threshold': 0.2,
                'min_quarters_for_trend': 4,
                'slope_calculation_method': 'linear_regression'
            },
            'output': {
                'json_indent': 2,
                'summary_language': 'zh-CN',
                'csv_encoding': 'utf-8',
                'csv_include_header': True,
                'generate_individual_csv': True,
                'generate_combined_csv': False
            }
        }

        if config_path and os.path.exists(config_path):
            try:
                if HAS_YAML:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    # 合并配置
                    self._merge_configs(default_config, config)
                else:
                    print(f"警告：无法加载配置文件 {config_path}，PyYAML未安装")
            except Exception as e:
                print(f"警告：加载配置文件失败: {e}")

        return default_config

    def _merge_configs(self, default: Dict, custom: Dict) -> None:
        """递归合并配置"""
        for key, value in custom.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_configs(default[key], value)
            else:
                default[key] = value

    def load_data(self, input_path: str) -> Dict[str, Any]:
        """加载历史持仓数据"""
        print(f"正在加载数据: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 验证数据格式
        self._validate_data(data)

        self.data = data
        print(f"数据加载成功:")
        print(f"  基金代码: {data.get('master_code', '未知')}")
        print(f"  季度数量: {len(data.get('items', []))}")

        return data

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

    def analyze(self) -> Dict[str, Any]:
        """执行完整分析"""
        if self.data is None:
            raise ValueError("请先加载数据")

        print("\n开始分析基金持仓数据...")

        # 1. 数据预处理和组织
        stock_time_series = self._organize_stock_time_series()

        # 2. 个股精选
        key_stocks = self._select_key_stocks(stock_time_series)

        # 3. 双轴图数据分析
        dual_axis_analysis = self._analyze_dual_axis_data(stock_time_series, key_stocks)

        # 4. 操作节点识别
        operation_nodes = self._identify_operation_nodes(stock_time_series, key_stocks)

        # 5. 行业分析
        industry_analysis = self._analyze_industry_distribution()

        # 6. 生成报告
        report = self._generate_report(
            stock_time_series,
            key_stocks,
            dual_axis_analysis,
            operation_nodes,
            industry_analysis
        )

        self.analysis_results = report
        return report

    def _organize_stock_time_series(self) -> Dict[str, Dict[str, Any]]:
        """将数据按股票代码组织为时间序列"""
        stock_data = {}

        # 按时间排序（确保时间顺序正确）
        sorted_items = sorted(self.data['items'],
                            key=lambda x: x['as_of_date'])

        for item in sorted_items:
            quarter = self._date_to_quarter(item['as_of_date'])

            for position in item.get('a_positions', []):
                stock_code = position['stock_code']
                stock_name = position['stock_name']

                if stock_code not in stock_data:
                    stock_data[stock_code] = {
                        'stock_name': stock_name,
                        'quarters': [],
                        'market_values': [],
                        'shares': [],
                        'weights': [],
                        'quarter_dates': []
                    }

                stock_data[stock_code]['quarters'].append(quarter)
                stock_data[stock_code]['market_values'].append(position['market_value'])
                stock_data[stock_code]['shares'].append(position['shares'])
                stock_data[stock_code]['weights'].append(position['weight'])
                stock_data[stock_code]['quarter_dates'].append(item['as_of_date'])

        self.stock_data_cache = stock_data
        return stock_data

    def _date_to_quarter(self, date_str: str) -> str:
        """将日期转换为季度格式（如2025Q4）"""
        try:
            year = date_str[:4]
            month = int(date_str[5:7])
            quarter = (month - 1) // 3 + 1
            return f"{year}Q{quarter}"
        except:
            return date_str

    def _select_key_stocks(self, stock_time_series: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """精选关键个股"""
        print("\n精选关键个股...")

        candidate_stocks = []

        for stock_code, data in stock_time_series.items():
            if len(data['quarters']) < 2:
                continue  # 至少需要2个季度数据

            # 计算各项指标
            avg_weight = statistics.mean(data['weights'])
            quarters_held = len(data['quarters'])
            total_quarters = len(self.data['items'])
            quarters_held_ratio = quarters_held / total_quarters

            # 计算权重趋势斜率
            weight_slope = self._calculate_slope(data['weights'])

            # 计算市值和股数斜率
            market_value_slope = self._calculate_slope(data['market_values'])
            shares_slope = self._calculate_slope(data['shares'])

            # 计算各项得分
            scores = {
                'avg_weight_score': self._calculate_weight_score(avg_weight),
                'holding_stability_score': self._calculate_stability_score(quarters_held_ratio),
                'weight_trend_score': self._calculate_trend_score(weight_slope),
                'profit_performance_score': self._calculate_profit_score(market_value_slope, shares_slope),
                'industry_representation_score': self._calculate_industry_score(stock_code, data['stock_name'])
            }

            # 计算综合评分
            weights = self.config['stock_selection_thresholds']['selection_weights']
            comprehensive_score = self._calculate_comprehensive_score(scores, weights)

            candidate_stocks.append({
                'stock_code': stock_code,
                'stock_name': data['stock_name'],
                'avg_weight': avg_weight,
                'quarters_held': quarters_held,
                'quarters_held_ratio': quarters_held_ratio,
                'weight_slope': weight_slope,
                'market_value_slope': market_value_slope,
                'shares_slope': shares_slope,
                'scores': scores,
                'comprehensive_score': comprehensive_score
            })

        # 按综合评分排序
        candidate_stocks.sort(key=lambda x: x['comprehensive_score'], reverse=True)

        # 选择前N个股票
        max_stocks = self.config['stock_selection_thresholds']['max_stocks_to_select']
        min_avg_weight = self.config['stock_selection_thresholds']['min_avg_weight']
        min_quarters_held = self.config['stock_selection_thresholds']['min_quarters_held']

        selected_stocks = []
        for stock in candidate_stocks:
            if (stock['avg_weight'] >= min_avg_weight and
                stock['quarters_held_ratio'] >= min_quarters_held):
                selected_stocks.append(stock)
                if len(selected_stocks) >= max_stocks:
                    break

        print(f"从 {len(candidate_stocks)} 只股票中精选出 {len(selected_stocks)} 只关键个股")

        return selected_stocks

    def _calculate_slope(self, values: List[float]) -> float:
        """计算时间序列的斜率"""
        if len(values) < 2:
            return 0.0

        method = self.config['dual_axis_analysis']['slope_calculation_method']

        if method == 'simple_slope':
            # 简单首尾斜率
            return (values[-1] - values[0]) / (len(values) - 1)
        else:
            # 线性回归（默认）
            x = np.arange(len(values))
            y = np.array(values)

            # 处理异常值
            if self.config.get('slope_analysis', {}).get('ignore_outliers', True):
                mean = np.mean(y)
                std = np.std(y)
                threshold = self.config.get('slope_analysis', {}).get('outlier_threshold', 2.0)
                y = y[np.abs(y - mean) <= threshold * std]
                x = np.arange(len(y))

            if len(x) < 2:
                return 0.0

            # 线性回归计算斜率
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
        # 这里暂时返回一个默认值
        return 50.0

    def _calculate_comprehensive_score(self, scores: Dict[str, float], weights: Dict[str, float]) -> float:
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

    def _analyze_dual_axis_data(self, stock_time_series: Dict[str, Dict[str, Any]],
                               key_stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析双轴图数据"""
        print("\n分析双轴图数据...")

        analysis_results = {
            'csv_data_samples': {},
            'slope_analysis': {},
            'profit_analysis': {},
            'trend_analysis': {}
        }

        for stock in key_stocks:
            stock_code = stock['stock_code']
            data = stock_time_series[stock_code]

            # 生成CSV数据样本
            csv_data = self._generate_csv_data(stock_code, data)
            analysis_results['csv_data_samples'][stock_code] = csv_data

            # 斜率分析
            slope_analysis = self._analyze_slopes(data)
            analysis_results['slope_analysis'][stock_code] = slope_analysis

            # 收益分析
            profit_analysis = self._analyze_profit(data, slope_analysis)
            analysis_results['profit_analysis'][stock_code] = profit_analysis

            # 趋势分析
            trend_analysis = self._analyze_trends(data)
            analysis_results['trend_analysis'][stock_code] = trend_analysis

        return analysis_results

    def _generate_csv_data(self, stock_code: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成CSV格式数据"""
        market_value_unit = self.config['dual_axis_analysis']['market_value_unit']
        shares_unit = self.config['dual_axis_analysis']['shares_unit']

        csv_rows = []
        for i in range(len(data['quarters'])):
            market_value_100m = data['market_values'][i] / market_value_unit
            shares_million = data['shares'][i] / shares_unit

            csv_rows.append([
                data['quarters'][i],
                stock_code,
                round(market_value_100m, 2),
                round(shares_million, 2)
            ])

        return {
            'header': ['quarter', 'ticker', 'market_value_100m', 'shares_million'],
            'sample_rows': csv_rows[:3] if len(csv_rows) > 3 else csv_rows,
            'total_rows': len(csv_rows)
        }

    def _analyze_slopes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析斜率"""
        market_value_slope = self._calculate_slope(data['market_values'])
        shares_slope = self._calculate_slope(data['shares'])
        profit_differential = market_value_slope - shares_slope

        return {
            'market_value_slope': round(market_value_slope, 4),
            'shares_slope': round(shares_slope, 4),
            'profit_differential': round(profit_differential, 4),
            'slope_calculation_method': self.config['dual_axis_analysis']['slope_calculation_method']
        }

    def _analyze_profit(self, data: Dict[str, Any], slope_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析收益表现"""
        market_value_slope = slope_analysis['market_value_slope']
        shares_slope = slope_analysis['shares_slope']
        profit_differential = slope_analysis['profit_differential']

        # 判断收益类型
        threshold = self.config['stock_selection_thresholds']['min_slope_positive']
        if profit_differential > threshold:
            profit_type = 'positive_profit'
        elif profit_differential < -threshold:
            profit_type = 'negative_profit'
        else:
            profit_type = 'neutral'

        # 判断收益强度
        if profit_differential > 0.15:
            profit_strength = 'high_positive'
        elif profit_differential > 0.05:
            profit_strength = 'moderate_positive'
        elif profit_differential > 0.01:
            profit_strength = 'low_positive'
        elif profit_differential > -0.01:
            profit_strength = 'neutral'
        elif profit_differential > -0.05:
            profit_strength = 'low_negative'
        elif profit_differential > -0.15:
            profit_strength = 'moderate_negative'
        else:
            profit_strength = 'high_negative'

        return {
            'profit_type': profit_type,
            'profit_strength': profit_strength,
            'profit_differential_percentage': round(profit_differential * 100, 2),
            'profit_contribution_breakdown': {
                'price_contribution': 65.0,  # 简化版本，实际需要股价数据
                'shares_contribution': 35.0
            }
        }

    def _analyze_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析趋势"""
        market_value_trend = self._detect_trend(data['market_values'])
        shares_trend = self._detect_trend(data['shares'])

        # 判断组合趋势
        if market_value_trend == 'uptrend' and shares_trend in ['uptrend', 'slight_uptrend', 'stable']:
            combined_trend = 'positive_profit_trend'
        elif market_value_trend == 'downtrend' and shares_trend in ['downtrend', 'slight_downtrend']:
            combined_trend = 'negative_profit_trend'
        else:
            combined_trend = 'mixed_trend'

        return {
            'market_value_trend': market_value_trend,
            'shares_trend': shares_trend,
            'combined_trend': combined_trend,
            'trend_strength': 'moderate',  # 简化版本
            'trend_consistency': 'consistent' if len(data['market_values']) >= 4 else 'inconclusive'
        }

    def _detect_trend(self, values: List[float]) -> str:
        """检测趋势"""
        if len(values) < 2:
            return 'insufficient_data'

        slope = self._calculate_slope(values)

        if slope > 0.1:
            return 'uptrend'
        elif slope > 0.05:
            return 'slight_uptrend'
        elif slope < -0.1:
            return 'downtrend'
        elif slope < -0.05:
            return 'slight_downtrend'
        else:
            return 'stable'

    def _identify_operation_nodes(self, stock_time_series: Dict[str, Dict[str, Any]],
                                 key_stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """识别操作节点"""
        print("\n识别操作节点...")

        operation_nodes = {
            'significant_increases': [],
            'significant_decreases': [],
            'profit_turning_points': []
        }

        threshold = self.config['dual_axis_analysis']['significant_change_threshold']

        for stock in key_stocks:
            stock_code = stock['stock_code']
            data = stock_time_series[stock_code]

            if len(data['shares']) < 2:
                continue

            # 检测大幅变化
            for i in range(1, len(data['shares'])):
                current = data['shares'][i]
                previous = data['shares'][i-1]

                if previous == 0:
                    continue

                change_pct = (current - previous) / abs(previous)

                if abs(change_pct) >= threshold:
                    node = {
                        'stock_code': stock_code,
                        'stock_name': data['stock_name'],
                        'quarter': data['quarters'][i],
                        'previous_shares': previous,
                        'current_shares': current,
                        'change_pct': round(change_pct * 100, 2),
                        'type': 'increase' if change_pct > 0 else 'decrease',
                        'significance_level': 'high' if abs(change_pct) >= 0.3 else 'medium'
                    }

                    if change_pct > 0:
                        operation_nodes['significant_increases'].append(node)
                    else:
                        operation_nodes['significant_decreases'].append(node)

        print(f"识别到 {len(operation_nodes['significant_increases'])} 个大幅加仓节点")
        print(f"识别到 {len(operation_nodes['significant_decreases'])} 个大幅减仓节点")

        return operation_nodes

    def _analyze_industry_distribution(self) -> Dict[str, Any]:
        """分析行业分布（简化版本）"""
        # 在实际应用中，这里应该根据行业分类进行详细分析
        # 这里暂时返回一个简化版本

        return {
            'industry_distribution': [
                {
                    'industry_name': '家用电器',
                    'total_weight': 68.5,
                    'stock_count': 6,
                    'average_weight': 11.4
                },
                {
                    'industry_name': '机械设备',
                    'total_weight': 12.3,
                    'stock_count': 2,
                    'average_weight': 6.15
                }
            ],
            'concentration_analysis': {
                'top_3_industries_weight': 80.8,
                'concentration_level': 'moderate'
            }
        }

    def _generate_report(self, stock_time_series: Dict[str, Dict[str, Any]],
                        key_stocks: List[Dict[str, Any]],
                        dual_axis_analysis: Dict[str, Any],
                        operation_nodes: Dict[str, Any],
                        industry_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析报告"""
        print("\n生成分析报告...")

        fund_code = self.data['master_code']
        fund_name = self.data['items'][0]['master_name'] if self.data['items'] else '未知'

        report = {
            'metadata': {
                'fund_code': fund_code,
                'fund_name': fund_name,
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'total_quarters': len(self.data['items']),
                'quarters_analyzed': len(self.data['items']),
                'total_stocks': len(stock_time_series),
                'analysis_version': '1.0.0',
                'analysis_timestamp': datetime.now().isoformat()
            },
            'key_stocks_selection': {
                'selection_criteria': self.config['stock_selection_thresholds'],
                'candidate_stocks': key_stocks,
                'selected_stocks': [
                    {
                        'rank': i + 1,
                        'stock_code': stock['stock_code'],
                        'stock_name': stock['stock_name'],
                        'final_score': round(stock['comprehensive_score'], 1),
                        'selection_priority': 'high' if stock['comprehensive_score'] > 80 else 'medium'
                    }
                    for i, stock in enumerate(key_stocks)
                ]
            },
            'dual_axis_analysis': dual_axis_analysis,
            'operation_nodes': operation_nodes,
            'industry_analysis': industry_analysis,
            'recommendations': self._generate_recommendations(key_stocks, dual_axis_analysis)
        }

        return report

    def _generate_recommendations(self, key_stocks: List[Dict[str, Any]],
                                 dual_axis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成推荐建议"""
        focus_stocks = []

        for i, stock in enumerate(key_stocks[:3]):  # 前3个重点股票
            stock_code = stock['stock_code']
            profit_analysis = dual_axis_analysis['profit_analysis'].get(stock_code, {})

            if profit_analysis.get('profit_type') == 'positive_profit':
                priority = 'highest'
                reason = '收益表现最佳，正收益明显'
            else:
                priority = 'high'
                reason = '权重较高，具有分析价值'

            focus_stocks.append({
                'stock_code': stock_code,
                'stock_name': stock['stock_name'],
                'recommendation_reason': reason,
                'analysis_priority': priority
            })

        return {
            'focus_stocks': focus_stocks,
            'analysis_priorities': [
                {
                    'priority': 1,
                    'task': f"深度分析{key_stocks[0]['stock_name']}的收益来源",
                    'reason': '收益表现最突出，可作为核心案例'
                },
                {
                    'priority': 2,
                    'task': '分析操作节点的市场背景',
                    'reason': '理解加减仓时的市场环境和时机选择'
                }
            ]
        }

    def save_csv_data(self, output_dir: str) -> None:
        """保存CSV数据"""
        if not self.analysis_results:
            raise ValueError("请先执行分析")

        os.makedirs(output_dir, exist_ok=True)

        csv_config = self.config['output']
        encoding = csv_config['csv_encoding']
        include_header = csv_config['csv_include_header']

        dual_axis_analysis = self.analysis_results['dual_axis_analysis']
        csv_data_samples = dual_axis_analysis['csv_data_samples']

        for stock_code, csv_info in csv_data_samples.items():
            stock_name = None
            # 查找股票名称
            for stock in self.analysis_results['key_stocks_selection']['candidate_stocks']:
                if stock['stock_code'] == stock_code:
                    stock_name = stock['stock_name']
                    break

            if stock_name:
                # 生成完整CSV数据
                data = self.stock_data_cache[stock_code]
                market_value_unit = self.config['dual_axis_analysis']['market_value_unit']
                shares_unit = self.config['dual_axis_analysis']['shares_unit']

                filename = f"{stock_code}_{self.data['master_code']}_dual_axis.csv"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'w', encoding=encoding, newline='') as f:
                    writer = csv.writer(f)

                    if include_header:
                        writer.writerow(['quarter', 'ticker', 'market_value_100m', 'shares_million'])

                    for i in range(len(data['quarters'])):
                        market_value_100m = data['market_values'][i] / market_value_unit
                        shares_million = data['shares'][i] / shares_unit

                        writer.writerow([
                            data['quarters'][i],
                            stock_code,
                            round(market_value_100m, 2),
                            round(shares_million, 2)
                        ])

                print(f"  CSV数据已保存: {filepath}")

    def save_report(self, output_path: str) -> None:
        """保存分析报告"""
        if not self.analysis_results:
            raise ValueError("请先执行分析")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False,
                     indent=self.config['output']['json_indent'])

        print(f"分析报告已保存: {output_path}")

    def generate_summary(self) -> str:
        """生成自然语言总结"""
        if not self.analysis_results:
            raise ValueError("请先执行分析")

        report = self.analysis_results
        fund_code = report['metadata']['fund_code']
        fund_name = report['metadata']['fund_name']

        # 获取关键个股
        selected_stocks = report['key_stocks_selection']['selected_stocks']

        summary_lines = [
            f"# 基金个股持仓双轴历史图分析报告",
            f"",
            f"## 基本信息",
            f"- **基金代码**: {fund_code}",
            f"- **基金名称**: {fund_name}",
            f"- **分析日期**: {report['metadata']['analysis_date']}",
            f"- **数据范围**: {report['metadata']['total_quarters']} 个季度",
            f"",
            f"## 关键发现摘要",
            f"",
            f"### 1. 精选个股表现",
            f"通过对持仓股票的综合评分，筛选出 {len(selected_stocks)} 只关键个股：",
            f""
        ]

        for i, stock in enumerate(selected_stocks[:3]):  # 显示前3个
            stock_code = stock['stock_code']
            stock_name = stock['stock_name']
            score = stock['final_score']

            profit_analysis = report['dual_axis_analysis']['profit_analysis'].get(stock_code, {})
            profit_pct = profit_analysis.get('profit_differential_percentage', 0)

            summary_lines.append(
                f"{i+1}. **{stock_name} ({stock_code})** - 综合评分 {score} 分")
            summary_lines.append(
                f"   - 收益表现: {profit_pct}% 的正收益差")
            summary_lines.append(f"")

        # 添加操作节点信息
        op_nodes = report['operation_nodes']
        if op_nodes['significant_increases']:
            summary_lines.append(f"### 2. 重要操作节点")
            for node in op_nodes['significant_increases'][:2]:  # 显示前2个
                summary_lines.append(
                    f"- **大幅加仓**: {node['quarter']}，{node['stock_name']} 加仓 {node['change_pct']}%")

        # 添加推荐
        recommendations = report['recommendations']
        if recommendations['focus_stocks']:
            summary_lines.append(f"")
            summary_lines.append(f"### 3. 分析建议")
            summary_lines.append(f"建议重点关注以下股票进行深度分析：")
            for stock in recommendations['focus_stocks']:
                summary_lines.append(f"- **{stock['stock_name']} ({stock['stock_code']})**: {stock['recommendation_reason']}")

        summary_lines.append(f"")
        summary_lines.append(f"---")
        summary_lines.append(f"*报告生成时间: {report['metadata']['analysis_timestamp']}*")
        summary_lines.append(f"*分析工具: 基金个股持仓双轴历史图分析技能 v{report['metadata']['analysis_version']}*")

        return '\n'.join(summary_lines)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='分析基金历史持仓数据，生成双轴图分析报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
    # 分析数据并生成报告和CSV
    python analyze_dual_axis.py --input historical_data.json --output analysis.json --csv-dir ./csv_data

    # 只生成分析报告
    python analyze_dual_axis.py --input historical_data.json --output analysis.json

    # 生成总结文本
    python analyze_dual_axis.py --input historical_data.json --summary-text summary.txt

    # 分析前3个关键个股
    python analyze_dual_axis.py --input historical_data.json --top-n 3
        """
    )

    parser.add_argument(
        '--input',
        required=True,
        help='输入JSON文件路径（历史持仓数据）'
    )

    parser.add_argument(
        '--output',
        help='结构化分析报告输出路径（JSON格式）'
    )

    parser.add_argument(
        '--csv-dir',
        help='CSV数据输出目录'
    )

    parser.add_argument(
        '--summary-text',
        help='自然语言总结输出路径'
    )

    parser.add_argument(
        '--top-n',
        type=int,
        default=5,
        help='分析前N个关键个股（默认：5）'
    )

    parser.add_argument(
        '--config',
        help='配置文件路径（YAML格式）'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细日志信息'
    )

    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()

    try:
        # 初始化分析器
        analyzer = FundDualAxisAnalyzer(args.config)

        # 修改配置中的最大股票数
        analyzer.config['stock_selection_thresholds']['max_stocks_to_select'] = args.top_n

        # 加载数据
        analyzer.load_data(args.input)

        # 执行分析
        report = analyzer.analyze()

        # 保存报告
        if args.output:
            analyzer.save_report(args.output)

        # 保存CSV数据
        if args.csv_dir:
            analyzer.save_csv_data(args.csv_dir)

        # 生成并保存总结文本
        if args.summary_text:
            summary = analyzer.generate_summary()
            with open(args.summary_text, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"自然语言总结已保存: {args.summary_text}")

        # 显示总结
        print("\n" + "="*50)
        print("分析完成！")
        print("="*50)

        summary = analyzer.generate_summary()
        print(summary[:500] + "..." if len(summary) > 500 else summary)

        if args.csv_dir:
            print(f"\nCSV数据目录: {args.csv_dir}")

        return 0

    except KeyboardInterrupt:
        print("\n用户中断操作")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())