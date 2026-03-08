#!/usr/bin/env python3
"""
基金持仓数据一键获取与分析脚本

集成了数据获取和数据分析功能，提供一站式分析解决方案
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# 添加脚本目录到路径，以便导入其他模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fetch_data import FundDataFetcher
    from analyze_data import FundHeatmapAnalyzer
except ImportError:
    # 如果在同一目录下，可以直接导入
    pass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FundAnalysisPipeline:
    """基金分析流水线"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化流水线

        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.fetcher = FundDataFetcher()
        self.analyzer = FundHeatmapAnalyzer()

    def run_pipeline(self, fund_code: str, output_dir: str = "./reports") -> Dict[str, Any]:
        """
        运行完整的分析流水线

        Args:
            fund_code: 基金代码
            output_dir: 输出目录

        Returns:
            分析结果
        """
        logger.info(f"开始分析基金 {fund_code}")

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{fund_code}_{timestamp}"

        # 1. 获取数据
        logger.info("步骤1: 获取基金持仓数据")
        try:
            data = self.fetcher.fetch_fund_data(fund_code)

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
        logger.info("步骤3: 分析持仓数据")
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

        # 5. 生成博客大纲
        logger.info("步骤5: 生成博客大纲")
        try:
            blog_outline = self._generate_blog_outline(analysis_results, fund_code)

            # 保存博客大纲
            outline_file = os.path.join(output_dir, f"{base_filename}_blog_outline.md")
            with open(outline_file, 'w', encoding='utf-8') as f:
                f.write(blog_outline)
            logger.info(f"博客大纲已保存: {outline_file}")

        except Exception as e:
            logger.error(f"博客大纲生成失败: {e}")
            # 不阻止整个流程继续

        # 6. 生成摘要报告
        logger.info("步骤6: 生成摘要报告")
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

        # 7. 生成元数据文件
        logger.info("步骤7: 生成元数据文件")
        try:
            metadata = self._generate_metadata(fund_code, timestamp, {
                "raw_data": raw_data_file,
                "analysis": analysis_file,
                "summary": summary_file,
                "blog_outline": outline_file if 'outline_file' in locals() else None,
                "brief": brief_file if 'brief_file' in locals() else None
            })

            # 保存元数据
            metadata_file = os.path.join(output_dir, f"{base_filename}_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"元数据已保存: {metadata_file}")

        except Exception as e:
            logger.error(f"元数据生成失败: {e}")
            # 不阻止整个流程继续

        # 返回结果
        results = {
            "fund_code": fund_code,
            "timestamp": timestamp,
            "files": {
                "raw_data": raw_data_file,
                "analysis": analysis_file,
                "summary": summary_file,
                "blog_outline": outline_file if 'outline_file' in locals() else None,
                "brief": brief_file if 'brief_file' in locals() else None,
                "metadata": metadata_file if 'metadata_file' in locals() else None
            },
            "analysis_results": analysis_results
        }

        logger.info(f"基金 {fund_code} 分析流水线完成")
        return results

    def _generate_blog_outline(self, analysis_results: Dict[str, Any], fund_code: str) -> str:
        """
        生成博客大纲

        Args:
            analysis_results: 分析结果
            fund_code: 基金代码

        Returns:
            博客大纲
        """
        metadata = analysis_results.get("metadata", {})
        heatmap_signals = analysis_results.get("heatmap_signals", {})
        overall_color = analysis_results.get("overall_color", {})
        portfolio_score = analysis_results.get("portfolio_score", {})

        # 获取关键信号
        strong_buy_heavy = heatmap_signals.get("strong_buy_heavy", [])
        strong_sell_heavy = heatmap_signals.get("strong_sell_heavy", [])

        # 确定标题角度
        title_angle = ""
        if strong_buy_heavy and strong_sell_heavy:
            title_angle = "共识与分歧"
        elif strong_buy_heavy:
            title_angle = "重仓看好"
        elif strong_sell_heavy:
            title_angle = "投资争议"
        elif overall_color.get("is_red"):
            title_angle = "风险警示"
        else:
            title_angle = "持仓分析"

        # 构建博客大纲
        outline = f"""# {fund_code}持仓分析：{title_angle}的投资启示

## 1. 开篇：热力图全景一览
[插入持仓热力图截图]
说明：色块大小代表仓位权重，颜色代表AI综合评级
读者引导：点击图片→跳转工具页面查看实时数据

## 2. 关键信号解读：大师与AI的共识与分歧
"""

        # 添加共识点
        if strong_buy_heavy:
            stock_names = [s.get("stock_name") for s in strong_buy_heavy[:3]]
            outline += f"- **共识点**：{', '.join(stock_names)}为何同时获得重仓和AI看好？\n"

        # 添加分歧点
        if strong_sell_heavy:
            stock_names = [s.get("stock_name") for s in strong_sell_heavy[:2]]
            outline += f"- **分歧点**：{', '.join(stock_names)}的重仓逻辑与AI看空原因分析\n"

        outline += """
## 3. 财务指标深度分析
- 估值分析：PE/PB分位数，哪些股票被低估？
- 动量分析：涨幅与振幅，谁在强势上升通道？
- 流动性：换手率与成交量，机构关注度如何？

## 4. AI投资建议汇总
- 操作建议分布：持有/买入/卖出比例
- 置信度分析：AI判断的把握度如何？
- 目标价空间：哪些股票上涨潜力最大？

## 5. 行业分布与赛道选择
- 行业集中度：大师重点布局哪些赛道？
- 细分龙头：各行业中的代表性公司
- 趋势判断：行业配置背后的逻辑

## 6. 综合评估与风险评估
"""

        # 添加评分
        final_score = portfolio_score.get("final_score", 0)
        interpretation = portfolio_score.get("score_interpretation", "")
        outline += f"- 组合评分：{final_score:.1f}/100（{interpretation}）\n"

        # 添加风险提示
        if overall_color.get("is_red"):
            red_percentage = overall_color.get("red_percentage", 0)
            outline += f"- 风险警示：整体持仓偏红，{red_percentage:.1f}%股票被AI看空\n"

        outline += """
## 7. 投资建议与行动指南
- 重点关注：[列出重点股票]
- 操作建议：适合的投资者类型与策略
- 后续跟踪：需要关注的关键指标和时间点

## 附录：数据来源与方法说明
- 数据来源：ai2alpha.cn基金持仓热力图
- 分析时间：{analysis_date}
- 免责声明：本文为数据分析，不构成投资建议
""".format(analysis_date=metadata.get("analysis_date", datetime.now().isoformat()))

        return outline

    def _generate_brief_report(self, analysis_results: Dict[str, Any]) -> str:
        """
        生成摘要报告

        Args:
            analysis_results: 分析结果

        Returns:
            摘要报告
        """
        metadata = analysis_results.get("metadata", {})
        heatmap_signals = analysis_results.get("heatmap_signals", {})
        portfolio_score = analysis_results.get("portfolio_score", {})

        fund_code = metadata.get("fund_code", "unknown")
        total_stocks = metadata.get("total_stocks", 0)
        final_score = portfolio_score.get("final_score", 0)
        interpretation = portfolio_score.get("score_interpretation", "")

        # 关键信号统计
        strong_buy_heavy = len(heatmap_signals.get("strong_buy_heavy", []))
        strong_sell_heavy = len(heatmap_signals.get("strong_sell_heavy", []))

        brief = f"""# {fund_code}持仓分析摘要

## 核心发现
- **分析股票**：{total_stocks} 只
- **综合评分**：{final_score:.1f}/100（{interpretation}）
- **关键信号**：{strong_buy_heavy} 只重仓看好，{strong_sell_heavy} 只重仓看空

## 重点关注
"""

        # 添加重点关注股票
        if strong_buy_heavy > 0:
            stocks = heatmap_signals.get("strong_buy_heavy", [])[:3]
            for i, stock in enumerate(stocks):
                brief += f"{i+1}. **{stock.get('stock_name')}**（{stock.get('stock_code')}）\n"
                brief += f"   权重：{stock.get('weight')}%，AI评级：{stock.get('ai_rating')}\n"
                brief += f"   上涨空间：{stock.get('upside_potential', 0):.1f}%\n"

        brief += """
## 投资建议
1. **重点关注**：重仓且AI看好的股票
2. **深入研究**：重仓但AI看空的分歧点
3. **风险控制**：注意整体持仓的AI评级分布

## 后续跟踪
- 季度财报发布
- 行业政策变化
- AI评级更新

---
*报告生成时间：{timestamp}*
*数据来源：ai2alpha.cn*
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return brief

    def _generate_metadata(self, fund_code: str, timestamp: str, files: Dict[str, str]) -> Dict[str, Any]:
        """
        生成元数据

        Args:
            fund_code: 基金代码
            timestamp: 时间戳
            files: 文件路径字典

        Returns:
            元数据
        """
        return {
            "fund_code": fund_code,
            "analysis_timestamp": timestamp,
            "pipeline_version": "1.0.0",
            "generated_files": files,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform
            }
        }

    def print_results_summary(self, results: Dict[str, Any]) -> None:
        """
        打印结果摘要

        Args:
            results: 分析结果
        """
        fund_code = results.get("fund_code", "unknown")
        files = results.get("files", {})
        analysis_results = results.get("analysis_results", {})

        metadata = analysis_results.get("metadata", {})
        heatmap_signals = analysis_results.get("heatmap_signals", {})
        portfolio_score = analysis_results.get("portfolio_score", {})

        total_stocks = metadata.get("total_stocks", 0)
        final_score = portfolio_score.get("final_score", 0)
        interpretation = portfolio_score.get("score_interpretation", "")

        strong_buy_heavy = len(heatmap_signals.get("strong_buy_heavy", []))
        strong_sell_heavy = len(heatmap_signals.get("strong_sell_heavy", []))

        print("\n" + "="*60)
        print(f"基金分析流水线完成: {fund_code}")
        print("="*60)

        print(f"\n[Summary]")
        print(f"   股票数量: {total_stocks} 只")
        print(f"   综合评分: {final_score:.1f}/100 ({interpretation})")
        print(f"   关键信号: {strong_buy_heavy} 重仓看好, {strong_sell_heavy} 重仓看空")

        print(f"\n[Files]")
        for file_type, file_path in files.items():
            if file_path and os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"   {file_type}: {file_path} ({file_size:.1f} KB)")

        print(f"\n[Next Steps]")
        print("   1. 查看 summary.txt 获取分析总结")
        print("   2. 查看 blog_outline.md 获取博客大纲")
        print("   3. 使用分析结果进行内容创作")

        if strong_buy_heavy > 0:
            stocks = heatmap_signals.get("strong_buy_heavy", [])[:2]
            print(f"\n[Focus]")
            for stock in stocks:
                print(f"   • {stock.get('stock_name')} ({stock.get('stock_code')})")

        print("="*60)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='基金持仓数据一键获取与分析')
    parser.add_argument('--fund-code', '-c', required=True, help='基金代码')
    parser.add_argument('--output-dir', '-o', default='./reports', help='输出目录')
    parser.add_argument('--verbose', '-v', action='store_true', help='输出详细信息')
    parser.add_argument('--no-blog-outline', action='store_true', help='不生成博客大纲')
    parser.add_argument('--no-brief', action='store_true', help='不生成摘要报告')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # 初始化流水线
        pipeline = FundAnalysisPipeline()

        # 运行流水线
        results = pipeline.run_pipeline(
            fund_code=args.fund_code,
            output_dir=args.output_dir
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
