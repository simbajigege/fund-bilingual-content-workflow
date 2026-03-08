#!/usr/bin/env python3
"""
基金历史持仓权重堆叠图分析工具 - 主入口点

提供统一的命令行接口，集成数据获取、分析、报告生成等功能。
"""

import argparse
import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description='基金历史持仓权重堆叠图分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 快速分析基金159730，生成完整报告
  %(prog)s quick --fund-code 159730 --output-dir ./reports

  # 分步分析
  %(prog)s fetch --fund-code 159730 --output data.json --quarters 8
  %(prog)s analyze --input data.json --output stacked.csv --report analysis.json
  %(prog)s blog --report analysis.json --output blog.md --template 7segment

  # 使用示例数据测试
  %(prog)s test --sample
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # quick 命令：快速分析
    quick_parser = subparsers.add_parser('quick', help='一站式快速分析')
    quick_parser.add_argument('--fund-code', '-c', required=True, help='基金代码')
    quick_parser.add_argument('--output-dir', '-o', default='./reports', help='输出目录')
    quick_parser.add_argument('--quarters', '-q', type=int, default=8,
                             help='分析的季度数（默认：8，0表示全部）')
    quick_parser.add_argument('--verbose', '-v', action='store_true', help='输出详细信息')

    # fetch 命令：获取数据
    fetch_parser = subparsers.add_parser('fetch', help='获取基金多季度持仓数据')
    fetch_parser.add_argument('--fund-code', '-c', required=True, help='基金代码')
    fetch_parser.add_argument('--output', '-o', default='historical_data.json', help='输出文件路径')
    fetch_parser.add_argument('--quarters', '-q', type=int, default=0,
                             help='提取的季度数（0表示全部）')
    fetch_parser.add_argument('--validate', '-v', action='store_true', help='验证数据完整性')
    fetch_parser.add_argument('--verbose', action='store_true', help='输出详细信息')

    # analyze 命令：分析数据
    analyze_parser = subparsers.add_parser('analyze', help='分析历史持仓权重')
    analyze_parser.add_argument('--input', '-i', required=True, help='输入JSON文件路径')
    analyze_parser.add_argument('--output', '-o', help='堆叠图数据输出路径（CSV格式）')
    analyze_parser.add_argument('--report', '-r', help='结构化分析报告输出路径（JSON格式）')
    analyze_parser.add_argument('--summary', '-s', help='自然语言总结输出路径')
    analyze_parser.add_argument('--min-weight', type=float, default=0.5,
                               help='最小权重阈值（默认：0.5%%，低于此值忽略）')
    analyze_parser.add_argument('--verbose', '-v', action='store_true', help='输出详细信息')

    # blog 命令：生成博客内容
    blog_parser = subparsers.add_parser('blog', help='生成博客内容框架')
    blog_parser.add_argument('--report', '-r', required=True, help='分析报告文件路径')
    blog_parser.add_argument('--output', '-o', help='博客内容输出路径')
    blog_parser.add_argument('--template', '-t', default='7segment',
                            choices=['7segment', 'simple', 'detailed'],
                            help='模板类型（默认：7segment）')
    blog_parser.add_argument('--verbose', '-v', action='store_true', help='输出详细信息')

    # test 命令：测试
    test_parser = subparsers.add_parser('test', help='测试功能')
    test_parser.add_argument('--sample', action='store_true', help='使用示例数据测试')
    test_parser.add_argument('--fund-code', '-c', help='使用真实基金代码测试（需要网络）')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='输出详细信息')

    # version 命令
    subparsers.add_parser('version', help='显示版本信息')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    try:
        if args.command == 'quick':
            from scripts.quick_analysis import QuickAnalysisPipeline
            pipeline = QuickAnalysisPipeline()
            results = pipeline.run_pipeline(
                fund_code=args.fund_code,
                output_dir=args.output_dir,
                quarters=args.quarters if args.quarters > 0 else 0
            )
            pipeline.print_results_summary(results)
            return 0

        elif args.command == 'fetch':
            from scripts.fetch_historical_data import FundHistoricalDataFetcher
            fetcher = FundHistoricalDataFetcher()
            data = fetcher.fetch_historical_data(args.fund_code)

            if args.validate:
                if fetcher.validate_data(data):
                    logger.info("数据验证通过")
                else:
                    logger.warning("数据验证发现警告")

            if args.quarters > 0:
                data = fetcher.extract_recent_quarters(data, args.quarters)

            fetcher.save_to_file(data, args.output)

            # 输出摘要信息
            items = data.get("items", [])
            print(f"\n数据获取成功!")
            print(f"基金代码: {args.fund_code}")
            print(f"季度数量: {len(items)}")
            print(f"输出文件: {args.output}")
            return 0

        elif args.command == 'analyze':
            from scripts.analyze_historical_weights import HistoricalWeightsAnalyzer

            analyzer = HistoricalWeightsAnalyzer()
            # 更新最小权重阈值
            analyzer.config["weight_thresholds"]["min_weight"] = args.min_weight

            data = analyzer.load_data(args.input)
            analysis_results = analyzer.analyze(data)

            # 保存堆叠图数据
            if args.output:
                stacked_data = analysis_results.get("stacked_chart_data", [])
                if stacked_data:
                    analyzer.save_stacked_chart_data(stacked_data, args.output)
                    print(f"堆叠图数据已保存: {args.output}")
                else:
                    logger.warning("没有堆叠图数据可生成")

            # 保存分析报告
            if args.report:
                import json
                with open(args.report, 'w', encoding='utf-8') as f:
                    json.dump(analysis_results, f, ensure_ascii=False, indent=2)
                print(f"分析报告已保存: {args.report}")

            # 保存自然语言总结
            if args.summary:
                summary = analyzer.generate_summary(analysis_results)
                with open(args.summary, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"自然语言总结已保存: {args.summary}")

            # 输出关键结果
            metadata = analysis_results.get("metadata", {})
            stability = analysis_results.get("stability_analysis", {})
            style = analysis_results.get("style_assessment", {})

            print(f"\n分析完成!")
            print(f"基金: {metadata.get('fund_name', '未知')}")
            print(f"季度: {len(metadata.get('quarters_analyzed', []))}个")
            print(f"股票: {metadata.get('unique_stocks', 0)}只")
            print(f"稳定性: {stability.get('overall_stability_score', 0):.1f}/100")
            print(f"风格: {style.get('type', '未知')}")
            print(f"换手率: {style.get('turnover_rate', 0):.1f}%")
            return 0

        elif args.command == 'blog':
            from scripts.generate_blog_content import BlogContentGenerator

            generator = BlogContentGenerator()
            analysis_report = generator.load_analysis_report(args.report)
            blog_content = generator.generate_blog_content(analysis_report, args.template)

            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(blog_content)
                print(f"博客内容已保存: {args.output}")

                # 输出统计信息
                word_count = len(blog_content.split())
                section_count = blog_content.count("## ")
                print(f"博客统计: {word_count}字, {section_count}个主要部分")
            else:
                print(blog_content)
            return 0

        elif args.command == 'test':
            if args.sample:
                # 使用示例数据测试
                sample_file = os.path.join(os.path.dirname(__file__), 'examples', 'sample_data.json')
                if not os.path.exists(sample_file):
                    print(f"示例文件不存在: {sample_file}")
                    return 1

                # 运行示例测试
                from examples.test_sample import test_sample_data
                test_sample_data()
                return 0
            elif args.fund_code:
                # 使用真实数据测试（简化版）
                from scripts.fetch_historical_data import FundHistoricalDataFetcher
                from scripts.analyze_historical_weights import HistoricalWeightsAnalyzer

                fetcher = FundHistoricalDataFetcher()
                analyzer = HistoricalWeightsAnalyzer()

                print(f"测试基金: {args.fund_code}")
                print("1. 获取数据...")
                data = fetcher.fetch_historical_data(args.fund_code)
                data = fetcher.extract_recent_quarters(data, 4)  # 只取最近4个季度

                print("2. 分析数据...")
                analysis_results = analyzer.analyze(data)

                metadata = analysis_results.get("metadata", {})
                print(f"\n测试完成!")
                print(f"基金: {metadata.get('fund_name', '未知')}")
                print(f"季度: {len(metadata.get('quarters_analyzed', []))}个")
                print(f"股票: {metadata.get('unique_stocks', 0)}只")
                return 0
            else:
                print("请指定 --sample 或 --fund-code 参数")
                return 1

        elif args.command == 'version':
            print("基金历史持仓权重堆叠图分析工具 v1.0.0")
            print("数据来源: ai2alpha.cn基金多季度持仓数据")
            return 0

    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        logger.error("请确保已安装依赖: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.error(f"命令执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())