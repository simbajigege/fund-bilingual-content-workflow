#!/usr/bin/env python3
"""
基金多季度持仓数据获取脚本

从ai2alpha.cn API获取基金多季度持仓明细数据
API端点：/api/v1/masters/by-master-code/{fund_code}
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FundHistoricalDataFetcher:
    """基金历史数据获取器"""

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

    def fetch_historical_data(self, fund_code: str) -> Dict[str, Any]:
        """
        获取基金多季度持仓数据

        Args:
            fund_code: 基金代码

        Returns:
            基金多季度持仓数据

        Raises:
            requests.RequestException: API请求失败
            ValueError: 数据格式错误或API返回错误
        """
        url = f"{self.base_url}/masters/by-master-code/{fund_code}"

        logger.info(f"获取基金 {fund_code} 的多季度持仓数据")
        logger.debug(f"请求URL: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # 检查数据格式
            if "master_code" not in data:
                raise ValueError("API返回数据格式错误：缺少master_code字段")

            if "items" not in data:
                raise ValueError("API返回数据格式错误：缺少items字段")

            logger.info(f"成功获取基金 {fund_code} 的多季度持仓数据，共 {len(data.get('items', []))} 个季度数据")

            # 添加元数据
            data["_metadata"] = {
                "fetched_at": datetime.now().isoformat(),
                "fund_code": fund_code,
                "api_url": url,
                "total_quarters": len(data.get("items", [])),
                "quarters": self._extract_quarters(data.get("items", []))
            }

            return data

        except requests.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise ValueError(f"响应不是有效的JSON: {e}")

    def _extract_quarters(self, items: List[Dict[str, Any]]) -> List[str]:
        """
        从items中提取季度列表

        Args:
            items: 季度数据列表

        Returns:
            季度标识列表
        """
        quarters = []
        for item in items:
            as_of_date = item.get("as_of_date")
            if as_of_date:
                quarter = self._date_to_quarter(as_of_date)
                if quarter:
                    quarters.append(quarter)
        return sorted(quarters, reverse=True)  # 最近季度在前

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

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        验证数据完整性

        Args:
            data: 要验证的数据

        Returns:
            验证是否通过
        """
        required_fields = ["master_code", "items", "total"]

        # 检查顶层字段
        for field in required_fields:
            if field not in data:
                logger.error(f"缺少顶层字段: {field}")
                return False

        items = data.get("items", [])
        if not isinstance(items, list):
            logger.error("items字段不是列表")
            return False

        if len(items) == 0:
            logger.warning("items列表为空")
            return True  # 空数据也算有效，可能是新基金

        # 检查每个季度的数据
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                logger.error(f"第{i}个季度数据不是字典")
                return False

            # 检查必需字段
            required_item_fields = ["master_code", "as_of_date", "a_positions"]
            for field in required_item_fields:
                if field not in item:
                    logger.warning(f"第{i}个季度数据缺少字段: {field}")

            # 检查持仓数据
            a_positions = item.get("a_positions", [])
            if not isinstance(a_positions, list):
                logger.error(f"第{i}个季度数据的a_positions不是列表")
                return False

            # 检查持仓股票数据
            for j, position in enumerate(a_positions):
                if not isinstance(position, dict):
                    logger.error(f"第{i}个季度第{j}个持仓数据不是字典")
                    continue  # 继续检查其他持仓

                required_position_fields = ["stock_code", "stock_name", "weight"]
                for field in required_position_fields:
                    if field not in position:
                        logger.warning(f"第{i}个季度第{j}个持仓缺少字段: {field}")

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

    def extract_recent_quarters(self, data: Dict[str, Any], num_quarters: int = 8) -> Dict[str, Any]:
        """
        提取最近N个季度的数据

        Args:
            data: 原始数据
            num_quarters: 要提取的季度数

        Returns:
            最近N个季度的数据
        """
        items = data.get("items", [])

        if not items:
            logger.warning("没有季度数据可提取")
            return data

        # 按as_of_date排序（最近在前）
        sorted_items = sorted(
            items,
            key=lambda x: x.get("as_of_date", ""),
            reverse=True
        )

        # 取前N个季度
        recent_items = sorted_items[:num_quarters]

        # 构建返回数据
        result = {
            "master_code": data.get("master_code"),
            "items": recent_items,
            "total": len(recent_items),
            "_metadata": {
                **data.get("_metadata", {}),
                "extracted_quarters": num_quarters,
                "original_total": len(items)
            }
        }

        logger.info(f"提取了最近 {num_quarters} 个季度的数据，共 {len(recent_items)} 个季度")

        return result

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='获取基金多季度持仓数据')
    parser.add_argument('--fund-code', '-c', required=True, help='基金代码')
    parser.add_argument('--output', '-o', default='historical_data.json', help='输出文件路径')
    parser.add_argument('--quarters', '-q', type=int, default=0,
                       help='提取的季度数（0表示全部）')
    parser.add_argument('--validate', '-v', action='store_true', help='验证数据完整性')
    parser.add_argument('--verbose', action='store_true', help='输出详细信息')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # 初始化获取器
        fetcher = FundHistoricalDataFetcher()

        # 获取数据
        data = fetcher.fetch_historical_data(args.fund_code)

        # 验证数据
        if args.validate:
            if fetcher.validate_data(data):
                logger.info("数据验证通过")
            else:
                logger.warning("数据验证发现警告")

        # 提取指定季度数的数据
        if args.quarters > 0:
            data = fetcher.extract_recent_quarters(data, args.quarters)

        # 保存数据
        fetcher.save_to_file(data, args.output)

        # 输出摘要信息
        items = data.get("items", [])
        total = data.get("total", 0)
        metadata = data.get("_metadata", {})

        print(f"\n数据获取成功!")
        print(f"基金代码: {args.fund_code}")
        print(f"季度数量: {len(items)}")
        print(f"总数据量: {total}")
        print(f"输出文件: {args.output}")

        # 显示季度信息
        quarters = metadata.get("quarters", [])
        if quarters:
            print(f"\n分析季度: {', '.join(quarters[:4])}... 共{len(quarters)}个季度")

        # 显示最近季度的持仓概况
        if items:
            latest_item = items[0]  # 最近季度
            a_positions = latest_item.get("a_positions", [])
            as_of_date = latest_item.get("as_of_date", "未知日期")

            print(f"\n最近季度 ({as_of_date}) 持仓概况:")
            print(f"  持仓股票数: {len(a_positions)}")

            if a_positions:
                total_weight = sum(p.get("weight", 0) for p in a_positions)
                print(f"  总权重: {total_weight:.2f}%")

                print(f"\n前3大持仓:")
                sorted_positions = sorted(a_positions, key=lambda x: x.get("weight", 0), reverse=True)
                for i, position in enumerate(sorted_positions[:3]):
                    print(f"  {i+1}. {position['stock_name']} ({position['stock_code']})")
                    print(f"     权重: {position['weight']}%")
                    print(f"     持仓股数: {position.get('shares', 'N/A')}")
                    print(f"     持仓市值: {position.get('market_value', 'N/A')}")

        return 0

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())