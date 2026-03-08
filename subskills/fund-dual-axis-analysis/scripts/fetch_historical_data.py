#!/usr/bin/env python3
"""
基金历史持仓数据获取脚本

功能：通过API获取基金多季度历史持仓数据，保存为JSON格式。
使用示例：
    python fetch_historical_data.py --fund-code 159730 --quarters 12 --output historical_data.json
"""

import argparse
import json
import sys
import os
import time
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime

# 添加项目根目录到Python路径，以便导入配置
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("警告：未安装PyYAML，将使用默认配置")

class FundDataFetcher:
    """基金数据获取器"""

    def __init__(self, config_path: Optional[str] = None):
        """初始化数据获取器"""
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'content-type': 'application/json',
            'language': 'cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'api': {
                'base_url': 'https://ai2alpha.cn/api/v1',
                'endpoint': '/masters/by-master-code/{master_code}',
                'timeout': 30,
                'retry_attempts': 3,
                'retry_delay': 1,
                'max_quarters': 20
            },
            'logging': {
                'level': 'INFO'
            }
        }

        if config_path and os.path.exists(config_path):
            try:
                if HAS_YAML:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    # 合并默认配置
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

    def fetch_fund_data(self, fund_code: str, max_quarters: Optional[int] = None) -> Dict[str, Any]:
        """
        获取基金历史持仓数据

        参数：
            fund_code: 基金代码
            max_quarters: 最大获取季度数（None表示使用配置中的默认值）

        返回：
            包含历史持仓数据的字典
        """
        if max_quarters is None:
            max_quarters = self.config['api']['max_quarters']

        endpoint = self.config['api']['endpoint'].format(master_code=fund_code)
        url = self.config['api']['base_url'] + endpoint

        print(f"正在获取基金 {fund_code} 的历史持仓数据...")
        print(f"API地址: {url}")
        print(f"最大获取季度数: {max_quarters}")

        try:
            response = self._make_request(url)
            data = response.json()

            # 验证数据格式
            self._validate_data(data, fund_code)

            # 限制返回的季度数
            if 'items' in data and len(data['items']) > max_quarters:
                print(f"警告：数据包含 {len(data['items'])} 个季度，限制为前 {max_quarters} 个季度")
                data['items'] = data['items'][:max_quarters]
                data['total'] = len(data['items'])

            print(f"成功获取 {len(data['items'])} 个季度的持仓数据")
            return data

        except Exception as e:
            print(f"获取数据失败: {e}")
            raise

    def _make_request(self, url: str) -> requests.Response:
        """发送HTTP请求，支持重试"""
        retry_attempts = self.config['api']['retry_attempts']
        retry_delay = self.config['api']['retry_delay']
        timeout = self.config['api']['timeout']

        for attempt in range(retry_attempts):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < retry_attempts - 1:
                    print(f"请求失败 (尝试 {attempt + 1}/{retry_attempts}): {e}")
                    time.sleep(retry_delay)
                else:
                    raise

    def _validate_data(self, data: Dict[str, Any], expected_fund_code: str) -> None:
        """验证数据格式"""
        if not isinstance(data, dict):
            raise ValueError("返回数据不是有效的JSON对象")

        required_fields = ['master_code', 'items', 'total']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"返回数据缺少必需字段: {field}")

        if data['master_code'] != expected_fund_code:
            raise ValueError(f"返回数据基金代码不匹配: 期望 {expected_fund_code}, 实际 {data['master_code']}")

        if not isinstance(data['items'], list):
            raise ValueError("items字段必须是列表")

        # 验证items中的每个季度数据
        for i, item in enumerate(data['items']):
            if not isinstance(item, dict):
                raise ValueError(f"items[{i}] 不是字典")

            item_required_fields = ['id', 'master_code', 'master_name', 'a_positions', 'as_of_date']
            for field in item_required_fields:
                if field not in item:
                    raise ValueError(f"items[{i}] 缺少必需字段: {field}")

            # 验证a_positions
            if not isinstance(item['a_positions'], list):
                raise ValueError(f"items[{i}].a_positions 不是列表")

            for j, position in enumerate(item['a_positions']):
                if not isinstance(position, dict):
                    raise ValueError(f"items[{i}].a_positions[{j}] 不是字典")

                position_required_fields = ['stock_code', 'stock_name', 'shares', 'market_value', 'weight']
                for field in position_required_fields:
                    if field not in position:
                        raise ValueError(f"items[{i}].a_positions[{j}] 缺少必需字段: {field}")

    def save_data(self, data: Dict[str, Any], output_path: str) -> None:
        """保存数据到JSON文件"""
        # 添加元数据
        data_with_metadata = {
            **data,
            'metadata': {
                'fetch_time': datetime.now().isoformat(),
                'fetch_tool': 'fund_dual_axis_analysis',
                'fetch_version': '1.0.0',
                'config_used': self.config
            }
        }

        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_with_metadata, f, ensure_ascii=False, indent=2)

        print(f"数据已保存到: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path) / 1024:.2f} KB")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='获取基金历史持仓数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
    # 获取基金159730的最近12个季度数据
    python fetch_historical_data.py --fund-code 159730 --quarters 12 --output data_159730.json

    # 使用自定义配置文件
    python fetch_historical_data.py --fund-code 159730 --config config.yaml --output data.json

    # 只获取最近4个季度数据
    python fetch_historical_data.py --fund-code 159730 --quarters 4
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
        help='获取的季度数（默认：12）'
    )

    parser.add_argument(
        '--output',
        default='historical_fund_data.json',
        help='输出文件路径（默认：historical_fund_data.json）'
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
        # 初始化数据获取器
        fetcher = FundDataFetcher(args.config)

        # 获取数据
        data = fetcher.fetch_fund_data(args.fund_code, args.quarters)

        # 保存数据
        fetcher.save_data(data, args.output)

        # 显示数据摘要
        print("\n" + "="*50)
        print("数据获取完成！")
        print("="*50)
        print(f"基金代码: {data['master_code']}")
        print(f"基金名称: {data['items'][0]['master_name'] if data['items'] else '未知'}")
        print(f"季度数量: {len(data['items'])}")

        if data['items']:
            # 统计股票数量
            all_stocks = set()
            for item in data['items']:
                for position in item['a_positions']:
                    all_stocks.add(f"{position['stock_code']} - {position['stock_name']}")

            print(f"股票数量: {len(all_stocks)}")

            # 显示时间范围
            dates = [item['as_of_date'] for item in data['items']]
            if dates:
                print(f"时间范围: {min(dates)} 至 {max(dates)}")

        print(f"输出文件: {args.output}")
        print("="*50)

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