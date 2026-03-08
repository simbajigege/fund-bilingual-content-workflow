#!/usr/bin/env python3
"""
基金历史持仓权重快速分析脚本

一站式获取多季度持仓数据并进行分析，生成完整报告
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuickAnalysisPipeline:
    """快速分析流水线"""

    def __init__(self):
        """初始化流水线"""
        try:
            from fetch_historical_data import FundHistoricalDataFetcher
            from analyze_historical_weights import HistoricalWeightsAnalyzer
            self.fetcher = FundHistoricalDataFetcher()
            self.analyzer = HistoricalWeightsAnalyzer()
        except ImportError as e:
            logger.error(f"导入模块失败: {e}")
            logger.error("请确保fetch_historical_data.py和analyze_historical_weights.py在同一目录下")
            raise

    def run_pipeline(self, fund_code: str, output_dir: str = "./reports",
                    quarters: int = 8) -> Dict[str, Any]:
        """
        运行完整的分析流水线

        Args:
            fund_code: 基金代码
            output_dir: 输出目录
            quarters: 分析的季度数

        Returns:
            分析结果
        """
        logger.info(f"开始快速分析基金 {fund_code}")

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{fund_code}_{timestamp}"

        # 1. 获取数据
        logger.info("步骤1: 获取基金多季度持仓数据")
        try:
            data = self.fetcher.fetch_historical_data(fund_code)

            # 提取指定季度数的数据
            if quarters > 0:
                data = self.fetcher.extract_recent_quarters(data, quarters)

            # 保存原始数据
            raw_data_file = os.path.join(output_dir, f"{base_filename}_raw.json")
            self.fetcher.save_to_file(data, raw_data_file)
            logger.info(f"原始数据已保存: {raw_data_file}")

        except Exception as e:
            logger.error(f"数据获取失败: {e}")
            raise

        # 2. 验证数据
        logger.info("步骤2: 验证数据完整性")
        if not self.fetcher.validate_data(data):
            logger.warning("数据验证发现警告，但将继续分析")

        # 3. 分析数据
        logger.info("步骤3: 分析历史持仓权重")
        try:
            analysis_results = self.analyzer.analyze(data)

            # 保存分析报告
            analysis_file = os.path.join(output_dir, f"{base_filename}_analysis.json")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, ensure_ascii=False, indent=2)
            logger.info(f"分析报告已保存: {analysis_file}")

        except Exception as e:
            logger.error(f"数据分析失败: {e}")
            raise

        # 4. 生成自然语言总结
        logger.info("步骤4: 生成自然语言总结")
        try:
            summary = self.analyzer.generate_summary(analysis_results)

            # 保存总结
            summary_file = os.path.join(output_dir, f"{base_filename}_summary.txt")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            logger.info(f"自然语言总结已保存: {summary_file}")

        except Exception as e:
            logger.error(f"总结生成失败: {e}")
            raise

        # 5. 生成堆叠图数据
        logger.info("步骤5: 生成堆叠图数据")
        try:
            stacked_data = analysis_results.get("stacked_chart_data", [])

            if stacked_data:
                stacked_file = os.path.join(output_dir, f"{base_filename}_stacked.csv")
                self.analyzer.save_stacked_chart_data(stacked_data, stacked_file)
                logger.info(f"堆叠图数据已保存: {stacked_file}")
            else:
                logger.warning("没有堆叠图数据可生成")

        except Exception as e:
            logger.error(f"堆叠图数据生成失败: {e}")
            # 不阻止整个流程继续

        # 6. 生成元数据文件
        logger.info("步骤6: 生成元数据文件")
        try:
            metadata = self._generate_metadata(fund_code, timestamp, quarters, {
                "raw_data": raw_data_file,
                "analysis": analysis_file,
                "summary": summary_file,
                "stacked_data": stacked_file if 'stacked_file' in locals() else None
            })

            # 保存元数据
            metadata_file = os.path.join(output_dir, f"{base_filename}_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"元数据已保存: {metadata_file}")

        except Exception as e:
            logger.error(f"元数据生成失败: {e}")
            # 不阻止整个流程继续

        # 7. 生成分析摘要
        logger.info("步骤7: 生成分析摘要")
        try:
            brief_report = self._generate_brief_report(analysis_results)

            # 保存摘要报告
            brief_file = os.path.join(output_dir, f"{base_filename}_brief.md")
            with open(brief_file, 'w', encoding='utf-8') as f:
                f.write(brief_report)
            logger.info(f"摘要报告已保存: {brief_file}")

        except Exception as e:
            logger.error(f"摘要报告生成失败: {e}")
            # 不阻止整个流程继续

        # 返回结果
        results = {
            "fund_code": fund_code,
            "timestamp": timestamp,
            "quarters_analyzed": quarters,
            "files": {
                "raw_data": raw_data_file,
                "analysis": analysis_file,
                "summary": summary_file,
                "stacked_data": stacked_file if 'stacked_file' in locals() else None,
                "metadata": metadata_file if 'metadata_file' in locals() else None,
                "brief": brief_file if 'brief_file' in locals() else None
            },
            "analysis_results": analysis_results
        }

        logger.info(f"基金 {fund_code} 快速分析流水线完成")
        return results

    def _generate_metadata(self, fund_code: str, timestamp: str, quarters: int,
                          files: Dict[str, str]) -> Dict[str, Any]:
        """
        生成元数据

        Args:
            fund_code: 基金代码
            timestamp: 时间戳
            quarters: 分析的季度数
            files: 文件路径字典

        Returns:
            元数据
        """
        return {
            "fund_code": fund_code,
            "analysis_timestamp": timestamp,
            "quarters_analyzed": quarters,
            "pipeline_version": "1.0.0",
            "generated_files": files,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform
            }
        }

    def _generate_brief_report(self, analysis_results: Dict[str, Any]) -> str:
        """
        生成摘要报告

        Args:
            analysis_results: 分析结果

        Returns:
            摘要报告
        """
        metadata = analysis_results.get("metadata", {})
        stability = analysis_results.get("stability_analysis", {})
        trend = analysis_results.get("trend_analysis", {})
        style = analysis_results.get("style_assessment", {})
        key_signals = analysis_results.get("key_signals", [])

        fund_code = metadata.get("fund_code", "unknown")
        fund_name = metadata.get("fund_name", "unknown")
        quarters = metadata.get("quarters_analyzed", [])
        unique_stocks = metadata.get("unique_stocks", 0)

        overall_stability = stability.get("overall_stability_score", 0)
        style_type = style.get("type", "unknown")
        style_interpretation = style.get("interpretation", "")
        turnover_rate = style.get("turnover_rate", 0)

        # 统计关键信号
        signal_counts = {
            "P0": 0,
            "P1": 0,
            "P2": 0
        }
        for signal in key_signals:
            priority = signal.get("priority", "")
            if priority in signal_counts:
                signal_counts[priority] += 1

        # 构建摘要报告
        brief = f"""# {fund_code}({fund_name})历史持仓分析摘要

## 核心发现
- **分析期间**：{len(quarters)}个季度（{quarters[0]} 至 {quarters[-1]}）
- **分析股票**：{unique_stocks}只
- **整体稳定性**：{overall_stability}/100
- **投资风格**：{style_type}（换手率{turnover_rate:.1f}%）
- **关键信号**：P0:{signal_counts['P0']}个, P1:{signal_counts['P1']}个, P2:{signal_counts['P2']}个

## 稳定性分析
"""

        high_stability = stability.get("high_stability_stocks", [])
        if high_stability:
            brief += "**高稳定性核心持仓：**\n"
            for stock in high_stability[:3]:
                brief += f"- {stock.get('stock_name', stock.get('stock_code'))}：{stock.get('stability_score')}分，平均权重{stock.get('avg_weight')}%\n"

        high_volatility = stability.get("high_volatility_stocks", [])
        if high_volatility:
            brief += "\n**高波动性持仓：**\n"
            for stock in high_volatility[:2]:
                brief += f"- {stock.get('stock_name', stock.get('stock_code'))}：仅{stock.get('stability_score')}分\n"

        brief += "\n## 变动趋势分析\n"

        increasing = trend.get("increasing_trend_stocks", [])
        if increasing:
            brief += "**持续加仓：**\n"
            for stock in increasing[:2]:
                brief += f"- {stock.get('stock_name', stock.get('stock_code'))}：权重{stock.get('current_weight')}%，变化{stock.get('weight_change')}%\n"

        decreasing = trend.get("decreasing_trend_stocks", [])
        if decreasing:
            brief += "\n**持续减仓：**\n"
            for stock in decreasing[:2]:
                brief += f"- {stock.get('stock_name', stock.get('stock_code'))}：权重{stock.get('current_weight')}%，变化{stock.get('weight_change')}%\n"

        new_entrants = trend.get("new_entrants", [])
        if new_entrants:
            brief += f"\n**新进持仓**：{len(new_entrants)}只\n"

        exited_stocks = trend.get("exited_stocks", [])
        if exited_stocks:
            brief += f"**退出持仓**：{len(exited_stocks)}只\n"

        brief += "\n## 关键信号（前3个）\n"
        if key_signals:
            for i, signal in enumerate(key_signals[:3]):
                stock_name = signal.get("stock_name", signal.get("stock_code"))
                desc = signal.get("description", "")
                priority = signal.get("priority", "")
                brief += f"{i+1}. **[{priority}] {stock_name}**：{desc}\n"
        else:
            brief += "无显著关键信号\n"

        brief += "\n## 投资建议\n"
        brief += f"**风格解读**：{style_interpretation}\n\n"

        brief += "**重点关注**：\n"
        if high_stability:
            stock_names = [s.get("stock_name", s.get("stock_code")) for s in high_stability[:2]]
            brief += f"1. 核心持仓：{', '.join(stock_names)}\n"

        if increasing:
            stock_names = [s.get("stock_name", s.get("stock_code")) for s in increasing[:1]]
            if stock_names:
                brief += f"2. 加仓趋势：{', '.join(stock_names)}\n"

        brief += "\n**风险提示**：\n"
        if turnover_rate > 20:
            brief += f"1. 换手率较高（{turnover_rate:.1f}%），注意13F数据滞后影响\n"
        if high_volatility:
            brief += f"2. 部分股票持仓波动大，跟踪需谨慎\n"
        brief += "3. 本文为数据分析，不构成投资建议\n"

        brief += f"\n---\n*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        brief += "*数据来源：ai2alpha.cn基金多季度持仓数据*\n"

        return brief

    def print_results_summary(self, results: Dict[str, Any]) -> None:
        """
        打印结果摘要

        Args:
            results: 分析结果
        """
        fund_code = results.get("fund_code", "unknown")
        files = results.get("files", {})
        analysis_results = results.get("analysis_results", {})
        quarters_analyzed = results.get("quarters_analyzed", 0)

        metadata = analysis_results.get("metadata", {})
        stability = analysis_results.get("stability_analysis", {})
        style = analysis_results.get("style_assessment", {})
        key_signals = analysis_results.get("key_signals", [])

        fund_name = metadata.get("fund_name", "unknown")
        unique_stocks = metadata.get("unique_stocks", 0)
        overall_stability = stability.get("overall_stability_score", 0)
        style_type = style.get("type", "unknown")
        turnover_rate = style.get("turnover_rate", 0)

        # 统计关键信号
        p0_signals = [s for s in key_signals if s.get("priority") == "P0"]
        p1_signals = [s for s in key_signals if s.get("priority") == "P1"]

        print("\n" + "="*60)
        print(f"基金历史持仓分析完成: {fund_code}({fund_name})")
        print("="*60)

        print(f"\n[Summary]")
        print(f"   分析季度: {quarters_analyzed}个")
        print(f"   分析股票: {unique_stocks}只")
        print(f"   整体稳定性: {overall_stability}/100")
        print(f"   投资风格: {style_type} (换手率{turnover_rate:.1f}%)")
        print(f"   关键信号: P0:{len(p0_signals)}个, P1:{len(p1_signals)}个")

        print(f"\n[Files]")
        for file_type, file_path in files.items():
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"   {file_type}: {os.path.basename(file_path)} ({file_size:.1f} KB)")

        print(f"\n[Next Steps]")
        print("   1. 查看 summary.txt 获取分析总结")
        print("   2. 查看 stacked.csv 获取堆叠图数据")
        print("   3. 查看 brief.md 获取投资摘要")
        print("   4. 使用分析结果进行内容创作")

        if p0_signals:
            print(f"\n[Focus] (P0 signals):")
            for signal in p0_signals[:2]:
                stock_name = signal.get("stock_name", signal.get("stock_code"))
                desc = signal.get("description", "")
                print(f"   • {stock_name}: {desc[:50]}...")

        print("="*60)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='基金历史持仓数据快速分析')
    parser.add_argument('--fund-code', '-c', required=True, help='基金代码')
    parser.add_argument('--output-dir', '-o', default='./reports', help='输出目录')
    parser.add_argument('--quarters', '-q', type=int, default=8,
                       help='分析的季度数（默认：8，0表示全部）')
    parser.add_argument('--verbose', '-v', action='store_true', help='输出详细信息')
    parser.add_argument('--no-brief', action='store_true', help='不生成摘要报告')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # 初始化流水线
        pipeline = QuickAnalysisPipeline()

        # 运行流水线
        results = pipeline.run_pipeline(
            fund_code=args.fund_code,
            output_dir=args.output_dir,
            quarters=args.quarters if args.quarters > 0 else 0
        )

        # 打印结果摘要
        pipeline.print_results_summary(results)

        return 0

    except KeyboardInterrupt:
        logger.info("用户中断操作")
        return 130
    except Exception as e:
        logger.error(f"流水线执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
