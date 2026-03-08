#!/usr/bin/env python3
"""
一站式基金数据获取与分析脚本

功能：获取基金历史持仓数据并立即进行分析，生成完整报告。
使用示例：
    python fetch_and_analyze.py --fund-code 159730 --report-dir ./reports --csv-dir ./csv_data
"""

import argparse
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入其他脚本的功能
try:
    from scripts.fetch_historical_data import FundDataFetcher
    from scripts.analyze_dual_axis import FundDualAxisAnalyzer
except ImportError:
    # 如果直接运行，可能需要调整导入路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fetch_historical_data import FundDataFetcher
    from analyze_dual_axis import FundDualAxisAnalyzer

class FundAnalysisPipeline:
    """基金分析流水线"""

    def __init__(self, config_path: str = None):
        """初始化流水线"""
        self.config_path = config_path
        self.fetcher = FundDataFetcher(config_path)
        self.analyzer = FundDualAxisAnalyzer(config_path)
        self.results = {}

    def run_pipeline(self, fund_code: str, quarters: int = 12,
                     report_dir: str = None, csv_dir: str = None,
                     top_n: int = 5) -> Dict[str, Any]:
        """
        运行完整分析流水线

        参数：
            fund_code: 基金代码
            quarters: 分析季度数
            report_dir: 报告输出目录
            csv_dir: CSV数据输出目录
            top_n: 分析前N个关键个股

        返回：
            包含所有结果的字典
        """
        print("="*60)
        print("基金个股持仓双轴历史图分析流水线")
        print("="*60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"基金代码: {fund_code}")
        print(f"分析季度数: {quarters}")
        print(f"关键个股数量: {top_n}")
        print("-"*60)

        # 步骤1：获取数据
        print("\n[步骤1/3] 获取历史持仓数据...")
        start_time = time.time()

        try:
            data = self.fetcher.fetch_fund_data(fund_code, quarters)
            fetch_time = time.time() - start_time
            print(f"✓ 数据获取成功 ({fetch_time:.2f}秒)")
            print(f"  季度数量: {len(data['items'])}")
        except Exception as e:
            print(f"[ERROR] 数据获取失败: {e}")
            raise

        # 步骤2：分析数据
        print("\n[步骤2/3] 分析持仓数据...")
        start_time = time.time()

        try:
            # 设置分析器配置
            self.analyzer.config['stock_selection_thresholds']['max_stocks_to_select'] = top_n

            # 加载和分析数据
            self.analyzer.data = data
            report = self.analyzer.analyze()
            analysis_time = time.time() - start_time
            print(f"✓ 数据分析成功 ({analysis_time:.2f}秒)")

            # 获取关键个股信息
            selected_stocks = report['key_stocks_selection']['selected_stocks']
            print(f"  精选个股数量: {len(selected_stocks)}")

            # 显示收益表现
            for stock in selected_stocks[:3]:  # 显示前3个
                stock_code = stock['stock_code']
                profit = report['dual_axis_analysis']['profit_analysis'].get(stock_code, {})
                profit_pct = profit.get('profit_differential_percentage', 0)
                print(f"  - {stock['stock_name']}: {profit_pct}% 收益差")
        except Exception as e:
            print(f"[ERROR] 数据分析失败: {e}")
            raise

        # 步骤3：生成输出
        print("\n[步骤3/3] 生成输出文件...")
        start_time = time.time()

        try:
            output_files = self._generate_outputs(
                fund_code, report, data,
                report_dir, csv_dir
            )
            output_time = time.time() - start_time
            print(f"✓ 输出生成成功 ({output_time:.2f}秒)")

            # 显示生成的文件
            for file_type, filepath in output_files.items():
                if filepath and os.path.exists(filepath):
                    size_kb = os.path.getsize(filepath) / 1024
                    print(f"  - {file_type}: {filepath} ({size_kb:.1f} KB)")

            # 保存结果
            self.results = {
                'fund_code': fund_code,
                'data': data,
                'report': report,
                'output_files': output_files,
                'timings': {
                    'fetch_time': fetch_time,
                    'analysis_time': analysis_time,
                    'output_time': output_time,
                    'total_time': fetch_time + analysis_time + output_time
                }
            }

            return self.results

        except Exception as e:
            print(f"[ERROR] 输出生成失败: {e}")
            raise

    def _generate_outputs(self, fund_code: str, report: Dict[str, Any],
                         data: Dict[str, Any], report_dir: str,
                         csv_dir: str) -> Dict[str, str]:
        """生成所有输出文件"""
        output_files = {}

        # 创建时间戳用于文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{fund_code}_analysis_{timestamp}"

        # 1. 保存原始数据（可选）
        if report_dir:
            os.makedirs(report_dir, exist_ok=True)

            raw_data_path = os.path.join(report_dir, f"{base_filename}_raw.json")
            with open(raw_data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            output_files['raw_data'] = raw_data_path

        # 2. 保存分析报告
        if report_dir:
            report_path = os.path.join(report_dir, f"{base_filename}_report.json")
            self.analyzer.save_report(report_path)
            output_files['analysis_report'] = report_path

        # 3. 保存自然语言总结
        if report_dir:
            summary = self.analyzer.generate_summary()
            summary_path = os.path.join(report_dir, f"{base_filename}_summary.txt")

            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)

            output_files['text_summary'] = summary_path

        # 4. 生成CSV数据
        if csv_dir:
            # 设置股票数据缓存（analyze方法中已经设置）
            self.analyzer.stock_data_cache = self._organize_stock_data(data)
            self.analyzer.save_csv_data(csv_dir)
            output_files['csv_data_dir'] = csv_dir

        # 5. 生成执行摘要
        if report_dir:
            executive_summary = self._generate_executive_summary(fund_code, report)
            exec_summary_path = os.path.join(report_dir, f"{base_filename}_executive.md")

            with open(exec_summary_path, 'w', encoding='utf-8') as f:
                f.write(executive_summary)

            output_files['executive_summary'] = exec_summary_path

        return output_files

    def _organize_stock_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """组织股票数据（从analyze_dual_axis.py复制）"""
        stock_data = {}

        sorted_items = sorted(data['items'], key=lambda x: x['as_of_date'])

        for item in sorted_items:
            quarter = self._date_to_quarter(item['as_of_date'])

            for position in (item.get('a_positions', []) + item.get('us_positions', []) + item.get('hk_positions', [])):
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

        return stock_data

    def _date_to_quarter(self, date_str: str) -> str:
        """将日期转换为季度格式"""
        try:
            year = date_str[:4]
            month = int(date_str[5:7])
            quarter = (month - 1) // 3 + 1
            return f"{year}Q{quarter}"
        except:
            return date_str

    def _generate_executive_summary(self, fund_code: str, report: Dict[str, Any]) -> str:
        """生成执行摘要"""
        fund_name = report['metadata']['fund_name']
        analysis_date = report['metadata']['analysis_date']

        # 获取关键信息
        selected_stocks = report['key_stocks_selection']['selected_stocks']
        op_nodes = report['operation_nodes']
        recommendations = report['recommendations']

        summary = f"""# 基金分析执行摘要

## 基本信息
- **基金代码**: {fund_code}
- **基金名称**: {fund_name}
- **分析日期**: {analysis_date}
- **分析季度数**: {report['metadata']['total_quarters']}
- **总股票数量**: {report['metadata']['total_stocks']}

## 核心发现

### 1. 关键个股表现
基于综合评分，以下个股值得重点关注：

"""

        for i, stock in enumerate(selected_stocks[:5]):  # 前5个
            stock_code = stock['stock_code']
            stock_name = stock['stock_name']
            score = stock['final_score']

            profit_analysis = report['dual_axis_analysis']['profit_analysis'].get(stock_code, {})
            profit_pct = profit_analysis.get('profit_differential_percentage', 0)
            profit_type = profit_analysis.get('profit_type', 'unknown')

            profit_icon = "UP" if profit_type == 'positive_profit' else "DOWN" if profit_type == 'negative_profit' else "FLAT"

            summary += f"{i+1}. **{stock_name} ({stock_code})** {profit_icon}\n"
            summary += f"   - 综合评分: {score}/100\n"
            summary += f"   - 收益表现: {profit_pct}% ({profit_type})\n"
            summary += f"   - 分析优先级: {stock['selection_priority'].upper()}\n\n"

        # 操作节点
        if op_nodes['significant_increases'] or op_nodes['significant_decreases']:
            summary += "### 2. 重大操作节点\n"

            for node in op_nodes['significant_increases'][:2]:
                summary += f"- **大幅加仓** ({node['quarter']}): {node['stock_name']} +{node['change_pct']}%\n"

            for node in op_nodes['significant_decreases'][:2]:
                summary += f"- **大幅减仓** ({node['quarter']}): {node['stock_name']} {node['change_pct']}%\n"

            summary += "\n"

        # 推荐建议
        if recommendations['focus_stocks']:
            summary += "### 3. 推荐分析重点\n"

            for stock in recommendations['focus_stocks'][:3]:
                summary += f"- **{stock['stock_name']} ({stock['stock_code']})**: {stock['recommendation_reason']}\n"

            summary += "\n"

        # 下一步行动
        summary += "## 下一步行动建议\n\n"

        for priority in recommendations['analysis_priorities']:
            summary += f"{priority['priority']}. {priority['task']}\n"
            summary += f"   *理由*: {priority['reason']}\n\n"

        # 数据文件
        summary += "## 生成的文件\n"
        summary += "- `*_report.json`: 完整分析报告（JSON格式）\n"
        summary += "- `*_summary.txt`: 自然语言总结\n"
        summary += "- `*_executive.md`: 执行摘要（本文件）\n"
        summary += "- `*_raw.json`: 原始数据备份\n"
        summary += "- `csv_data/`: 双轴图CSV数据目录\n"

        summary += f"\n---\n"
        summary += f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        summary += f"*分析工具: 基金个股持仓双轴历史图分析流水线*\n"

        return summary

    def print_results_summary(self):
        """打印结果摘要"""
        if not self.results:
            print("无分析结果")
            return

        results = self.results
        fund_code = results['fund_code']
        report = results['report']
        timings = results['timings']

        print("\n" + "="*60)
        print("分析结果摘要")
        print("="*60)

        print(f"🔍 **基金信息**")
        print(f"   代码: {fund_code}")
        print(f"   名称: {report['metadata']['fund_name']}")
        print(f"   季度数: {report['metadata']['total_quarters']}")

        print(f"\n[Data Analysis]")
        selected_stocks = report['key_stocks_selection']['selected_stocks']
        print(f"   关键个股: {len(selected_stocks)} 只")

        for i, stock in enumerate(selected_stocks[:3]):
            stock_code = stock['stock_code']
            profit = report['dual_axis_analysis']['profit_analysis'].get(stock_code, {})
            profit_pct = profit.get('profit_differential_percentage', 0)
            print(f"   {i+1}. {stock['stock_name']}: {profit_pct}% 收益差")

        print(f"\n⏱️ **性能指标**")
        print(f"   数据获取: {timings['fetch_time']:.2f}秒")
        print(f"   数据分析: {timings['analysis_time']:.2f}秒")
        print(f"   输出生成: {timings['output_time']:.2f}秒")
        print(f"   总耗时: {timings['total_time']:.2f}秒")

        print(f"\n💾 **输出文件**")
        output_files = results['output_files']
        for file_type, filepath in output_files.items():
            if filepath:
                if os.path.isdir(filepath):
                    print(f"   [DIR] {file_type}: {filepath}")
                else:
                    size_kb = os.path.getsize(filepath) / 1024 if os.path.exists(filepath) else 0
                    print(f"   [FILE] {file_type}: {filepath} ({size_kb:.1f} KB)")

        print("\n[DONE] 分析完成")
        print("="*60)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='一站式获取并分析基金历史持仓数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
    # 完整分析流程
    python fetch_and_analyze.py --fund-code 159730 --report-dir ./reports --csv-dir ./csv_data

    # 只分析最近8个季度
    python fetch_and_analyze.py --fund-code 159730 --quarters 8 --report-dir ./reports

    # 分析前3个关键个股
    python fetch_and_analyze.py --fund-code 159730 --top-n 3 --report-dir ./reports

    # 使用自定义配置文件
    python fetch_and_analyze.py --fund-code 159730 --config config.yaml --report-dir ./reports
        """
    )

    parser.add_argument(
        '--fund-code',
        required=True,
        help='基金代码（例如：159730）'
    )

    parser.add_argument(
        '--quarters',
        type=int,
        default=12,
        help='分析的季度数（默认：12）'
    )

    parser.add_argument(
        '--report-dir',
        default='./reports',
        help='报告输出目录（默认：./reports）'
    )

    parser.add_argument(
        '--csv-dir',
        default='./csv_data',
        help='CSV数据输出目录（默认：./csv_data）'
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
        # 创建输出目录
        os.makedirs(args.report_dir, exist_ok=True)
        os.makedirs(args.csv_dir, exist_ok=True)

        # 初始化流水线
        pipeline = FundAnalysisPipeline(args.config)

        # 运行流水线
        results = pipeline.run_pipeline(
            fund_code=args.fund_code,
            quarters=args.quarters,
            report_dir=args.report_dir,
            csv_dir=args.csv_dir,
            top_n=args.top_n
        )

        # 打印结果摘要
        pipeline.print_results_summary()

        return 0

    except KeyboardInterrupt:
        print("\n用户中断操作")
        return 1
    except Exception as e:
        print(f"\n错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
