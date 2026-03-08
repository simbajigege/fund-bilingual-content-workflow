#!/usr/bin/env python3
"""
基金持仓数据获取脚本

从ai2alpha.cn API获取基金持仓热力图数据
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FundDataFetcher:
    """基金数据获取器"""

    def __init__(self, base_url: str = "https://ai2alpha.cn/api/v1"):
        """
        初始化数据获取器

        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'content-type': 'application/json',
            'language': 'cn',
            'origin': 'https://ai2alpha.cn',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_fund_data(self, fund_code: str, limit: int = 200) -> Dict[str, Any]:
        """
        获取基金持仓数据

        Args:
            fund_code: 基金代码
            limit: 返回数据限制

        Returns:
            基金持仓数据

        Raises:
            requests.RequestException: API请求失败
            ValueError: 数据格式错误或API返回错误
        """
        url = f"{self.base_url}/stocks/ai-selected"

        payload = {
            "master_code": fund_code,
            "limit": limit
        }

        logger.info(f"获取基金 {fund_code} 的持仓数据")
        logger.debug(f"请求URL: {url}")
        logger.debug(f"请求载荷: {payload}")

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            if not data.get("success"):
                error_msg = data.get("error", "Unknown error")
                raise ValueError(f"API返回错误: {error_msg}")

            logger.info(f"成功获取基金 {fund_code} 的持仓数据，共 {len(data.get('data', []))} 条记录")

            # 添加元数据
            data["_metadata"] = {
                "fetched_at": datetime.now().isoformat(),
                "fund_code": fund_code,
                "api_url": url
            }

            return data

        except requests.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise ValueError(f"响应不是有效的JSON: {e}")

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        验证数据完整性

        Args:
            data: 要验证的数据

        Returns:
            验证是否通过
        """
        required_fields = ["success", "data", "meta"]

        # 检查顶层字段
        for field in required_fields:
            if field not in data:
                logger.error(f"缺少顶层字段: {field}")
                return False

        if not data["success"]:
            logger.error("API返回success=false")
            return False

        # 检查数据字段
        stocks = data.get("data", [])
        if not isinstance(stocks, list):
            logger.error("data字段不是列表")
            return False

        # 检查股票数据的基本字段
        for i, stock in enumerate(stocks):
            if not isinstance(stock, dict):
                logger.error(f"第{i}条股票数据不是字典")
                return False

            required_stock_fields = ["stock_code", "stock_name", "weight", "analysis_summary"]
            for field in required_stock_fields:
                if field not in stock:
                    logger.warning(f"股票 {stock.get('stock_code', f'index_{i}')} 缺少字段: {field}")

            # 检查analysis_summary
            analysis = stock.get("analysis_summary", {})
            required_analysis_fields = ["action", "target_price", "confidence", "risk_score"]
            for field in required_analysis_fields:
                if field not in analysis:
                    logger.warning(f"股票 {stock.get('stock_code', f'index_{i}')} 的analysis_summary缺少字段: {field}")

        return True

    def save_to_file(self, data: Dict[str, Any], filepath: str) -> None:
        """
        保存数据到文件

        Args:
            data: 要保存的数据
            filepath: 文件路径
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到: {filepath}")
        except IOError as e:
            logger.error(f"保存文件失败: {e}")
            raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='获取基金持仓数据')
    parser.add_argument('--fund-code', '-c', required=True, help='基金代码')
    parser.add_argument('--output', '-o', default='fund_data.json', help='输出文件路径')
    parser.add_argument('--limit', '-l', type=int, default=200, help='数据限制数量')
    parser.add_argument('--validate', '-v', action='store_true', help='验证数据完整性')
    parser.add_argument('--verbose', action='store_true', help='输出详细信息')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # 初始化获取器
        fetcher = FundDataFetcher()

        # 获取数据
        data = fetcher.fetch_fund_data(args.fund_code, args.limit)

        # 验证数据
        if args.validate:
            if fetcher.validate_data(data):
                logger.info("数据验证通过")
            else:
                logger.warning("数据验证发现警告")

        # 保存数据
        fetcher.save_to_file(data, args.output)

        # 输出摘要信息
        stocks = data.get("data", [])
        meta = data.get("meta", {})

        print(f"\n数据获取成功!")
        print(f"基金代码: {args.fund_code}")
        print(f"股票数量: {len(stocks)}")
        print(f"总持仓数: {meta.get('total_selected_codes', 'N/A')}")
        print(f"输出文件: {args.output}")

        # 显示前3只股票
        if stocks:
            print("\n前3只持仓股票:")
            for i, stock in enumerate(stocks[:3]):
                analysis = stock.get("analysis_summary", {})
                print(f"  {i+1}. {stock['stock_name']} ({stock['stock_code']})")
                print(f"     权重: {stock['weight']}%")
                print(f"     当前价: {stock.get('current_price', 'N/A')}")
                print(f"     AI建议: {analysis.get('action', 'N/A')}")
                print(f"     目标价: {analysis.get('target_price', 'N/A')}")

        return 0

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())