"""
重构后模块使用示例
展示新的模块化架构的使用方法
"""

import sys
import os
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.entity.processors.client_processor_new import ClientProcessorNew


def main():
    """主函数 - 演示重构后模块的使用"""
    
    # 示例日志数据
    sample_log_data = [
        "20240101 09:30:00.123 [INFO] Request: {'protocol': 'pb', 'service': 'rpc.trader.stock', 'cmd': 'query_account_asset', 'params': {'fund_token': 'ACCOUNT001'}, 'req_id': 'req_001'}",
        "20240101 09:30:01.456 [INFO] Response: {'result': {'account_asset': [{'available_value': 1000000, 'balance_value': 1000000, 'frozen_value': 0, 'market_value': 0, 'total_assets': 1000000, 'total_net_value': 1000000}]}, 'req_id': 'req_001'}",
        "20240101 09:31:00.789 [INFO] Request: {'protocol': 'pb', 'service': 'rpc.trader.stock', 'cmd': 'query_account_stock', 'params': {'fund_token': 'ACCOUNT001'}, 'req_id': 'req_002'}",
        "20240101 09:31:01.012 [INFO] Response: {'result': {'account_stock': [{'security_id': '000001', 'security_name': '平安银行', 'actual_amt': 1000, 'available_stock_balance': 1000, 'cost_price': 10.5, 'market_value': 10500, 'stock_balance': 1000}]}, 'req_id': 'req_002'}",
        "20240101 09:32:00.345 [INFO] Request: {'protocol': 'pb', 'service': 'rpc.trader.stock', 'cmd': 'query_order', 'params': {'fund_token': 'ACCOUNT001'}, 'req_id': 'req_003'}",
        "20240101 09:32:01.678 [INFO] Response: {'result': {'orders': [{'order_no': 'ORD001', 'symbol': '000001', 'symbol_name': '平安银行', 'price': 10.5, 'quantity': 100, 'order_status_msg': '已成交'}]}, 'req_id': 'req_003'}",
        "20240101 09:33:00.123 [INFO] Request: {'protocol': 'pb', 'service': 'rpc.trader.stock', 'cmd': 'query_trade', 'params': {'fund_token': 'ACCOUNT001'}, 'req_id': 'req_004'}",
        "20240101 09:33:01.456 [INFO] Response: {'result': {'trades': [{'trade_time': '20240101 09:30:00', 'order_no': 'ORD001', 'symbol': '000001', 'symbol_name': '平安银行', 'price': 10.5, 'quantity': 100, 'trade_amount': 1050, 'operation_msg': '买入'}]}, 'req_id': 'req_004'}",
        "20240101 09:33:00.901 [INFO] Request: {'protocol': 'json_funid', 'service': 'stockrzrq', 'cmd': '501001', 'params': {'fund_token': 'ACCOUNT002'}, 'req_id': 'req_005'}",
        "20240101 09:33:01.234 [INFO] Response: {'result': {'Array': [{'EnableBalance': 500000, 'AvailableValue': 500000, 'FinEnableQuota': 1000000, 'SloEnableQuota': 500000}]}, 'req_id': 'req_005'}",
        "20240101 09:34:00.567 [INFO] Request: {'protocol': 'json_funid', 'service': 'stockths', 'cmd': '610013', 'params': {'fund_token': 'ACCOUNT003'}, 'req_id': 'req_006'}",
        "20240101 09:34:01.890 [INFO] Response: {'result': {'Array': [{'TotalAssets': 2000000, 'AvailableValue': 2000000, 'GGT_SRZS': 2000000}]}, 'req_id': 'req_006'}"
    ]
    
    print("=== 重构后日志分析器使用示例 ===\n")
    
    # 初始化处理器
    print("1. 初始化处理器...")
    processor = ClientProcessorNew(sample_log_data)
    
    # 解析日志
    print("2. 解析日志数据...")
    processor.parse()
    
    # 显示处理汇总
    print("3. 显示处理汇总信息...")
    processor.show_processing_summary()
    
    # 显示请求统计
    print("\n4. 显示请求统计...")
    stats = processor.show_request_statics()
    for stat in stats:
        print(f"  {stat}")
    
    # 处理账户查询
    print("\n5. 处理账户查询...")
    accounts = processor.get_all_accounts()
    print(f"  发现账户: {accounts}")
    
    # 处理资金查询
    print("\n6. 处理资金查询...")
    fund_queries = processor.handle_fund_query()
    print(f"  资金查询结果: {fund_queries}")
    
    if fund_queries:
        print("  显示第一个资金查询结果:")
        processor.show_fund_query(fund_queries[0])
    
    # 处理持仓查询
    print("\n7. 处理持仓查询...")
    position_queries = processor.handle_position_query()
    print(f"  持仓查询结果: {position_queries}")
    
    if position_queries:
        print("  获取持仓查询时间:")
        query_times = processor.get_position_querytime(position_queries[0])
        print(f"  查询时间: {query_times}")
        
        if query_times:
            print("  显示第一个持仓查询结果:")
            processor.show_queryposition(position_queries[0], query_times[0])
    
    # 处理委托查询
    print("\n8. 处理委托查询...")
    order_queries = processor.handle_order_query()
    print(f"  委托查询结果: {order_queries}")
    
    if order_queries:
        print("  获取委托查询时间:")
        order_times = processor.get_order_querytime(order_queries[0])
        print(f"  查询时间: {order_times}")
        
        if order_times:
            print("  显示第一个委托查询结果:")
            processor.show_queryorder(order_queries[0], order_times[0])
    
    # 处理成交查询
    print("\n9. 处理成交查询...")
    trade_queries = processor.handle_trade_query()
    print(f"  成交查询结果: {trade_queries}")
    
    if trade_queries:
        print("  获取成交查询时间:")
        trade_times = processor.get_trade_querytime(trade_queries[0])
        print(f"  查询时间: {trade_times}")
        
        if trade_times:
            print("  显示第一个成交查询结果:")
            processor.show_querytrade(trade_queries[0], trade_times[0])
    
    # 获取处理汇总
    print("\n10. 获取完整处理汇总...")
    summary = processor.get_processing_summary()
    print(f"  统计信息: {summary['statistics']}")
    print(f"  账户信息: {summary['accounts']}")
    print(f"  资金信息: {summary['funds']}")
    print(f"  持仓信息: {summary['positions']}")
    print(f"  委托信息: {summary['orders']}")
    print(f"  成交信息: {summary['trades']}")
    
    # 导出数据
    print("\n11. 导出数据...")
    stats_df = processor.export_statistics_to_dataframe()
    print(f"  统计DataFrame形状: {stats_df.shape}")
    
    accounts_df = processor.export_accounts_to_dataframe()
    print(f"  账户DataFrame形状: {accounts_df.shape}")
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    main() 
