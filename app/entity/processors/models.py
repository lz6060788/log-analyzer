"""
数据模型定义
定义日志解析处理过程中使用的各种数据结构
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RequestPair:
    """请求对数据结构"""
    request: Dict[str, Any]
    response: Dict[str, Any]
    req_time: str
    rsp_time: str
    protocol: str


@dataclass
class QueryResult:
    """查询结果基础结构"""
    rsp_time: str
    fund: str
    req_id: str
    code: int
    message: str = ""


@dataclass
class FundQueryResult(QueryResult):
    """资金查询结果"""
    available_value: float = 0.0
    balance_value: float = 0.0
    frozen_value: float = 0.0
    market_value: float = 0.0
    total_assets: float = 0.0
    total_net_value: float = 0.0
    currency_msg: str = ""


@dataclass
class PositionQueryResult(QueryResult):
    """持仓查询结果"""
    security_id: str = ""
    security_name: str = ""
    actual_amt: float = 0.0
    available_stock_balance: float = 0.0
    cost_price: float = 0.0
    frozen_qty: float = 0.0
    market: str = ""
    market_name: str = ""
    market_price: float = 0.0
    market_value: float = 0.0
    stock_balance: float = 0.0
    yield_rate: float = 0.0


@dataclass
class OrderQueryResult(QueryResult):
    """委托查询结果"""
    symbol: str = ""
    symbol_name: str = ""
    market_name: str = ""
    operation_msg: str = ""
    price: float = 0.0
    quantity: float = 0.0
    trade_amount: float = 0.0
    avg_price: float = 0.0
    order_no: str = ""
    order_status_msg: str = ""
    order_type_msg: str = ""
    currency: str = ""


@dataclass
class TradeQueryResult(QueryResult):
    """成交查询结果"""
    trade_time: str = ""
    order_no: str = ""
    symbol: str = ""
    symbol_name: str = ""
    market_name: str = ""
    price: float = 0.0
    quantity: float = 0.0
    trade_amount: float = 0.0
    order_type_msg: str = ""
    operation_msg: str = ""
    currency: str = ""
    currency_msg: str = ""
    shareholder_account: str = ""


@dataclass
class BasketOrderResult:
    """篮子订单结果"""
    rsp_time: str
    instanceid: str
    source: str
    fund_num: int
    security_num: int
    side: str
    note: str


@dataclass
class AlgorithmOrderResult:
    """算法订单结果"""
    rsp_time: str
    fund: str
    inst_id: str
    inst_type: str
    security: str
    side: str
    qty: float
    price: float
    ptype: str
    pimit: float
    created_after: str
    expired_after: str
    price_fail_after: str


@dataclass
class ConditionOrderResult:
    """条件订单结果"""
    rsp_time: str
    fund: str
    basket_name: str
    order_from: str
    order_no: str
    side: str
    max_trigger_stock: int
    start_monitor_time: str
    end_monitor_time: str
    distribute_type: str


@dataclass
class PushMessage:
    """推送消息基础结构"""
    push_time: str
    message_type: str
    data: Dict[str, Any]


@dataclass
class BasketOrderPush(PushMessage):
    """篮子订单推送"""
    instance_id: str
    fund_token: str
    security_id: str
    market_id: str
    side: str
    order_price: float
    order_qty: float
    trade_volume: float
    order_id: str
    order_type_msg: str
    operation_msg: str
    order_time: str
    order_status_msg: str
    text: str = ""


@dataclass
class AlgorithmPush(PushMessage):
    """算法推送"""
    instruction_id: str
    action: str
    avg_px: float = 0.0
    qty: float = 0.0
    qty_left: float = 0.0
    qty_cancel: float = 0.0
    qty_trade: float = 0.0
    status_msg: str = ""
    msg: str = ""


@dataclass
class ConditionPush(PushMessage):
    """条件推送"""
    order_no: str
    symbol: str
    side: str
    condition: str
    status_msg: str
    trigger_time: str
    qty: float
    qty_order: float
    qty_trade: float
    algorithm_type: str


@dataclass
class StatisticsResult:
    """统计结果"""
    protocol: str
    servicename: str
    action: str
    counts: int
    avg_lens: str
    total_lens: str


@dataclass
class AccountInfo:
    """账户信息"""
    user_id: str
    fund_token: str
    account_code: str
    account_name: str
    alias: str
    broker_name: str
    broker_id: str
    trade_type: str


# 类型别名定义
RequestPairsDict = Dict[str, RequestPair]
QueryResultsDict = Dict[str, List[QueryResult]]
FundTokenMapping = Dict[str, str]
FundMapping = Dict[str, str]


class ProcessingConfig:
    """处理配置类"""
    
    def __init__(self):
        # 分割映射
        self.split_map = {
            "request": "&send=",
            "response": "&recv=",
        }
        
        # 请求时间映射
        self.req_time_map = {
            "request": "req_time",
            "response": "rsp_time"
        }
        
        # 跳过词汇
        self.skip_word = ['|timeout|']
        
        # 显示列配置
        self.columns = {
            "singleorder": ["rsp_time", "fund", "req_id", "order_source", "symbol", "price", "quantity", "side", "code"],
            "singleorder_failed": ["rsp_time", "fund", "req_id", "symbol", "code", "message"],
            "singleorder_cancel": ["rsp_time", "fund", "fund_token", "order_no", "exchange", "side", "code", "message"],
            "basketorder_cancel": ["rsp_time", "action", "InstanceID", "Supplement", "result"],
            "gradecondition_create": ["rsp_time", "fund", "basket_name", "order_from", "order_no", "side", "max_trigger_stock", "start_monitor_time", "end_monitor_time", "distribute_type"],
            "gradecondition_create_detail": ["fund", "condition", "algorithm_type", "exchange_type", "symbol", "balance", "qty", "side", "price", "price_type"],
            "gradecondition_operate": ["rsp_time", "action", "id", "order_no", "status_msg", "msg"],
            "gradecondition_push_instruction": ["rsp_time", "grade_status", "status_msg", "current_order_qty", "current_order_trigger_qty", "condition_size", "trade_order_qty", "traded_balance"],
            "gradecondition_push_condition": ["rsp_time", "symbol", "side", "condition", "status_msg", "trigger_time", "qty", "qty_order", "qty_trade", "algorithm_type"],
            "gradecondition_push_order": ["rsp_time", "OrderEntryTime", "SecurityID", "MarketID", "Side", "OrderID", "OrderPrice", "OrderQty", "OrderTypeMsg", "OrderStatusMsg", "Currency", "AvgPx"],
        }
        
        # 算法推送关键词
        self.possible_algorithm_pushkey = [
            "twap_instruction", "twap_order", "twap_trade",
            "twapplus_instruction", "twapplus_order", "twapplus_trade",
            "iceberg_instruction", "iceberg_order", "iceberg_trade",
        ]


class ProcessingState:
    """处理状态类"""
    
    def __init__(self):
        # 基础统计
        self.counts = 0
        self.counts_pb = 0
        self.counts_json = 0
        self.counts_funid = 0
        
        # 请求统计
        self.request_statics = {"pb": {}, "json": {}, "json_funid": {}}
        
        # 异常请求
        self.illegal_reqs = []
        self.timeout_reqs = []
        self.skipped_reqs = []
        self.new_transmit_reqs = []
        self.response_without_reqid = []
        self.lines_without_reqid = []
        self.skipped_reqpairs = {}
        
        # 用户信息
        self.userid = ""
        self.username = ""
        self.log_begin_time = ""
        self.log_end_time = ""
        
        # 映射关系
        self.fundtoken_dict = {}
        self.fund_dict = {}
        self.client_fundtoken_mapping = {}
        self.client_permissioncode_mapping = {} 
