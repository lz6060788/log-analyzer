"""
重构后的主控制器
整合所有模块，提供统一接口
"""

import pandas as pd
from typing import Dict, List, Any, Optional

from .base_processor import BaseProcessor
from .statistics_processor import StatisticsProcessor
from .account_processor import AccountProcessor
from .fund_processor import FundProcessor
from .position_processor import PositionProcessor
from .order_processor import OrderProcessor
from .trade_processor import TradeProcessor
from .ipo_processor import IPOProcessor
from .basket_processor import BasketProcessor
from .algorithm_processor import AlgorithmProcessor
from .condition_processor import ConditionProcessor
from .financing_processor import FinancingProcessor


class ClientProcessorNew:
    """重构后的客户端处理器主类"""

    def __init__(self, file_list: List[str], isJupyter: bool = True):
        """
        初始化处理器

        Args:
            file_list: 文件内容列表
        """
        # 设置pandas显示选项
        pd.set_option('display.max_rows', 50)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.float_format', '{:.2f}'.format)

        # 初始化基础处理器
        self.base_processor = BaseProcessor(isJupyter)
        self.state = self.base_processor.state
        self.req_pairs = self.base_processor.req_pairs

        # 存储文件列表
        self.file_list = file_list

    def parse(self) -> None:
        """
        解析日志文件
        """
        # 基础解析
        self.base_processor.parse(self.file_list)
        self.state = self.base_processor.state
        self.req_pairs = self.base_processor.req_pairs

        # 初始化各模块处理器
        self.statistics_processor = StatisticsProcessor(self.state, self.req_pairs)
        self.account_processor = AccountProcessor(self.state, self.req_pairs)
        self.fund_processor = FundProcessor(self.state, self.req_pairs)
        self.position_processor = PositionProcessor(self.state, self.req_pairs)
        self.order_processor = OrderProcessor(self.state, self.req_pairs)
        self.trade_processor = TradeProcessor(self.state, self.req_pairs)
        self.ipo_processor = IPOProcessor(self.state, self.req_pairs)
        self.basket_processor = BasketProcessor(self.state, self.req_pairs, self.base_processor)
        self.algorithm_processor = AlgorithmProcessor(self.state, self.req_pairs)
        self.condition_processor = ConditionProcessor(self.state, self.req_pairs, self.base_processor)
        self.financing_processor = FinancingProcessor(self.state, self.req_pairs)

        # 统计处理
        self.statistics_processor.parse_request_statistics()

        # 账户查询处理
        self.account_processor.parse_account_query()

        # 资金查询处理
        self.fund_processor.parse_fund_query()

        # 持仓查询处理
        self.position_processor.parse_position_query()

        # 委托查询处理
        self.order_processor.parse_order_query()

        # 成交查询处理
        self.trade_processor.parse_trade_query()

        # 新股申购查询处理
        self.ipo_processor.parse_ipo_query()
        self.ipo_processor.parse_ipo_lottery_query()

        # 篮子交易查询处理
        self.basket_processor.parse_basket_query()

        # 算法交易查询处理
        self.algorithm_processor.parse_algorithm_query()

        # 条件交易查询处理
        self.condition_processor.parse_condition_query()

        # 融资融券相关解析
        self.financing_processor.parse_financing_query()

    def filter_log_list(self, content: str = "", start_time: str = "", end_time: str = "") -> List[Any]:
        """
        过滤日志列表
        """
        self.base_processor.parse_log_list()
        if len(self.state.parsed_log_list) == 0:
            return []
        result = []
        if start_time == "" and end_time == "":
            result = self.state.parsed_log_list

        if start_time != "" and end_time != "":
            result = [log for log in self.state.parsed_log_list if log.time >= start_time and log.time <= end_time]

        if content != "":
            subStrList = content.split("~")
            result = [log for log in self.state.parsed_log_list if any(subStr in log.content for subStr in subStrList)]
        return result

    def show_request_statics(self) -> List[Dict[str, Any]]:
        """
        显示请求统计

        Returns:
            统计结果列表
        """
        return self.statistics_processor.show_request_statics()

    def show_processing_summary(self) -> None:
        """
        显示处理汇总信息
        """
        self.statistics_processor.show_processing_summary()
        self.account_processor.show_account_summary()
        self.fund_processor.show_fund_summary()
        self.position_processor.show_position_summary()
        self.order_processor.show_order_summary()
        self.trade_processor.show_trade_summary()
    
    def handle_account_query(self, req_time: str = "") -> Optional[pd.DataFrame]:
        """
        处理账户查询
        
        Args:
            req_time: 请求时间
            
        Returns:
            账户查询结果DataFrame
        """
        return self.account_processor.handle_account_query(req_time)
    
    def get_fund_by_fund_token(self, fund_token: str) -> str:
        """
        根据fund_token获取账户名称
        
        Args:
            fund_token: 资金令牌
            
        Returns:
            账户名称
        """
        return self.account_processor.get_fund_by_fund_token(fund_token)
    
    def get_request_list(self, protocol: str, servicename: str, cmd: str) -> List[str]:
        """
        获取请求列表
        
        Args:
            protocol: 协议类型
            servicename: 服务名称
            cmd: 命令
            
        Returns:
            请求ID列表
        """
        return self.base_processor.get_request_list(protocol, servicename, cmd)
    
    def get_all_accounts(self) -> List[str]:
        """
        获取所有账户列表
        
        Returns:
            账户列表
        """
        return self.account_processor.get_all_accounts()
    
    def export_statistics_to_dataframe(self) -> pd.DataFrame:
        """
        导出统计数据到DataFrame
        
        Returns:
            统计数据DataFrame
        """
        return self.statistics_processor.export_statistics_to_dataframe()
    
    def export_accounts_to_dataframe(self) -> pd.DataFrame:
        """
        导出账户信息到DataFrame
        
        Returns:
            账户信息DataFrame
        """
        return self.account_processor.export_accounts_to_dataframe()
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        获取处理汇总信息
        
        Returns:
            处理汇总字典
        """
        summary = {
            "statistics": self.statistics_processor.get_statistics_summary(),
            "accounts": self.account_processor.get_account_summary(),
            "funds": self.fund_processor.get_fund_summary(),
            "positions": self.position_processor.get_position_summary(),
            "orders": self.order_processor.get_order_summary(),
            "trades": self.trade_processor.get_trade_summary()
        }
        return summary

    def handle_fund_query(self) -> List[str]:
        """
        处理资金查询
        
        Returns:
            资金查询结果列表
        """
        return self.fund_processor.handle_fund_query()
    
    def handle_position_query(self) -> List[str]:
        """
        处理持仓查询
        
        Returns:
            持仓查询结果列表
        """
        return self.position_processor.handle_position_query()
    
    def handle_order_query(self) -> List[str]:
        """
        处理委托查询
        
        Returns:
            委托查询结果列表
        """
        return self.order_processor.handle_order_query()
    
    def get_fund_query_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        获取资金查询数据
        
        Returns:
            资金查询数据字典
        """
        return self.fund_processor.get_fund_query_data()
    
    # 持仓查询相关方法
    def get_position_querytime(self, fundkey: str) -> List[str]:
        """
        获取持仓查询时间列表
        
        Args:
            fundkey: 资金账户键值
            
        Returns:
            查询时间列表
        """
        return self.position_processor.get_position_querytime(fundkey)
    
    def get_position_query_data(self) -> Dict[str, Dict[str, Dict[str, pd.DataFrame]]]:
        """
        获取持仓查询数据
        
        Returns:
            持仓查询数据字典
        """
        return self.position_processor.get_position_query_data()
    
    # 委托查询相关方法
    def handle_order_query(self) -> List[str]:
        """
        处理委托查询
        
        Returns:
            委托查询结果列表
        """
        return self.order_processor.handle_order_query()

    def get_order_querytime(self, fundkey: str) -> List[str]:
        """
        获取委托查询时间列表
        
        Args:
            fundkey: 资金账户键值
            
        Returns:
            查询时间列表
        """
        return self.order_processor.get_order_querytime(fundkey)
    
    def get_order_query_data(self) -> Dict[str, Dict[str, Dict[str, pd.DataFrame]]]:
        """
        获取委托查询数据
        
        Returns:
            委托查询数据字典
        """
        return self.order_processor.get_order_query_data()
    def get_order_summary(self):
        return self.order_processor.get_order_summary()

    # 成交查询相关方法
    def handle_trade_query(self) -> List[str]:
        """
        处理成交查询
        
        Returns:
            成交查询结果列表
        """
        return self.trade_processor.handle_trade_query()

    def get_trade_querytime(self, fundkey: str) -> List[str]:
        """
        获取成交查询时间列表
        
        Args:
            fundkey: 资金账户键值
            
        Returns:
            查询时间列表
        """
        return self.trade_processor.get_trade_querytime(fundkey)

    def get_trade_query_data(self) -> Dict[str, Dict[str, Dict[str, pd.DataFrame]]]:
        """
        获取成交查询数据
        
        Returns:
            成交查询数据字典
        """
        return self.trade_processor.get_trade_query_data()

    def get_trade_summary(self):
        return self.trade_processor.get_trade_summary()

    # 新股申购相关接口
    def handle_ipo_query(self) -> List[str]:
        """
        处理新股申购额度查询，返回账户列表
        
        Returns:
            账户列表
        """
        return self.ipo_processor.handle_ipo_query()

    def handle_ipo_lottery_query(self) -> List[str]:
        """
        处理新股中签明细查询，返回账户列表
        
        Returns:
            账户列表
        """
        return self.ipo_processor.handle_ipo_lottery_query()

    def get_ipo_query_data(self, fund: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取新股申购额度查询数据
        
        Args:
            fund: 资金账户（可选）
        Returns:
            新股申购额度数据列表
        """
        return self.ipo_processor.get_ipo_query_data(fund)

    def get_ipo_lottery_data(self, fund: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取新股中签明细查询数据
        
        Args:
            fund: 资金账户（可选）
        Returns:
            新股中签明细数据列表
        """
        return self.ipo_processor.get_ipo_lottery_data(fund) 

    # 篮子交易相关接口
    def handle_basketorder(self) -> List[str]:
        """
        处理篮子订单查询
        
        Returns:
            篮子订单查询结果列表
        """
        return self.basket_processor.handle_basketorder()
    def get_basket_query_data(self, source: Optional[str] = None, fund: str = "", stockcode: str = "") -> List[Dict[str, Any]]:
        """
        获取篮子订单查询数据
        
        Args:
            source: 订单来源类型
            fund: 资金账户
            stockcode: 股票代码
        Returns:
            篮子订单数据列表
        """
        return self.basket_processor.get_basket_query_data(source, fund, stockcode)
    def get_basketorder_detail_data(self, instanceid: str) -> List[Dict[str, Any]]:
        """
        获取指定母单的篮子订单明细
        
        Args:
            instanceid: 母单ID
        Returns:
            篮子订单明细列表
        """
        return self.basket_processor.get_basketorder_detail_data(instanceid)
    def get_basket_summary_data(self, source: Optional[str] = None, fund: str = "", stockcode: str = "") -> List[Dict[str, Any]]:
        """
        获取篮子订单查询数据

        Args:
            querytime: 查询时间
        """
        return self.basket_processor.get_basket_summary_data(source,  fund, stockcode)

    def get_basket_instance_detail(self, instanceid: str) -> Dict[str, Any]:
        """
        获取指定母单的实例详情

        Args:
            instanceid: 母单ID
        """
        return self.basket_processor.get_basket_instance_detail(instanceid)

    def get_basket_order_detail(self, instanceid: str, fund: str = "", stockcode: str = "") -> Dict[str, Any]:
        """
        获取指定母单的全部子单详情

        Args:
            instanceid: 母单ID
            fund: 资金账户
            stockcode: 股票代码
        """
        return self.basket_processor.get_basket_order_detail(instanceid, fund, stockcode)

    def get_basket_query_data(self, querytime: str = None) -> List[Dict[str, Any]]:
        """
        获取篮子订单查询数据

        Args:
            querytime: 查询时间
        """
        return self.basket_processor.get_basket_query_data(querytime)

    def get_basket_initreqs(self, instance: str) -> Dict[str, Any]:
        """
        获取指定母单的原始请求明细

        Args:
            instance: 母单ID
        """
        return self.basket_processor.get_basket_initreqs(instance)

    def get_algorithm_code(self) -> List[str]:
        """
        获取算法订单涉及的股票代码列表
        
        Returns:
            股票代码列表
        """
        return self.algorithm_processor.get_algorithm_code()
    def get_algorithm_detail(self, instanceid: str) -> Optional[pd.DataFrame]:
        """
        获取指定算法订单的明细
        
        Args:
            instanceid: 算法单ID
        Returns:
            算法订单明细DataFrame
        """
        return self.algorithm_processor.get_algorithm_detail(instanceid)
    def get_algorithm_push_detail(self, instanceid: str, push_type: str):
        """
        获取算法订单推送明细
        
        Args:
            instanceid: 算法单ID
            push_type: 推送类型（如order、trade等）
        Returns:
            推送明细
        """
        return self.algorithm_processor.get_algorithm_push_detail(instanceid, push_type)
    def get_algorithm_query_data(self) -> List[Dict[str, Any]]:
        """
        获取算法订单查询数据
        
        Returns:
            算法订单数据列表
        """
        return self.algorithm_processor.get_algorithm_query_data() 
    def get_new_algorithm_order(self) -> List[Dict[str, Any]]:
        """
        获取当日新增的算法订单

        Returns:
            算法订单数据列表
        """
        return self.algorithm_processor.get_new_algorithm_order()

    # 条件交易相关接口
    def get_condition_summary_data(self) -> Dict[str, Any]:
        """
        获取条件单汇总数据
        
        Returns:
            条件单汇总数据字典
        """
        return self.condition_processor.get_condition_summary_data()
    def get_condition_instance_detail_data(self, order_no: str) -> Dict[str, Any]:
        """
        获取条件单实例明细数据
        
        Args:
            order_no: 母单编号
        Returns:
            条件单实例明细数据字典
        """
        return self.condition_processor.get_condition_instance_detail_data(order_no)
    def get_condition_order_detail_data(self, order_no: str) -> Any:
        """
        获取条件单母单操作明细数据
        
        Args:
            order_no: 母单编号
        Returns:
            条件单母单操作明细数据
        """
        return self.condition_processor.get_condition_order_detail_data(order_no)
    def get_condition_security_order_detail_data(self, order_no: str, fund: str, security: str) -> Any:
        """
        获取条件单证券操作明细数据
        
        Args:
            order_no: 母单编号
            fund: 资金账户
            security: 股票代码
        Returns:
            条件单证券操作明细数据
        """
        return self.condition_processor.get_condition_security_order_detail_data(order_no, fund, security)
    def get_condition_initreqs_data(self, order_no: str) -> Any:
        """
        获取条件单初始请求数据
        
        Args:
            order_no: 母单编号
        Returns:
            条件单初始请求数据
        """
        return self.condition_processor.get_condition_initreqs_data(order_no)
    def get_querycondition_data(self, querytime: str =  "") -> Any:
        """
        获取条件单查询数据
        
        Args:
            querytime: 查询时间
        Returns:
            条件单查询数据
        """
        return self.condition_processor.get_querycondition_data(querytime) 

    # 融资融券相关接口
    def get_finable_security_data(self, fund_key: Optional[str] = None) -> Dict[str, Any]:
        """
        获取可融资标的券数据（Web友好）
        
        Args:
            fund_key: 资金账户（可选）
        Returns:
            可融资标的券数据字典
        """
        return self.financing_processor.get_finable_security_data(fund_key)
    def get_finable_security_failed(self) -> List[Dict[str, Any]]:
        """
        获取可融资标的券失败查询（Web友好）
        
        Returns:
            失败查询列表
        """
        return self.financing_processor.get_finable_security_failed() 
    def handle_finable_security_query(self) -> List[str]:
        """
        汇总可融资标的券的资金账户列表
        
        Returns:
            资金账户fund_key列表
        """
        return self.financing_processor.handle_finable_security_query()
    def get_finable_security_querytime(self, fundkey: str) -> List[str]:
        """
        获取指定资金账户的可融资标的券查询时间列表
        
        Args:
            fundkey: 资金账户
        Returns:
            查询时间列表
        """
        return self.financing_processor.get_finable_security_querytime(fundkey) 
