"""
成交查询处理器模块
负责成交记录查询和处理
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from .models import TradeQueryResult, ProcessingState, RequestPairsDict


class TradeProcessor:
    """成交查询处理器类"""
    
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict):
        self.state = state
        self.req_pairs = req_pairs
        
        # 成交查询数据存储
        self.query_trade_dict = {}
        self.query_rzrq_trade_dict = {}
        self.query_ggt_trade_dict = {}
        self.query_trade_failed_list = []
        self.trade_querytime_reqid = {}
    
    def parse_trade_query(self) -> None:
        """
        解析成交查询数据
        """
        # 普通成交查询
        self._parse_normal_trade_query()
        
        # 信用成交查询
        self._parse_rzrq_trade_query()
        
        # 港股通成交查询
        self._parse_ggt_trade_query()
    
    def _parse_normal_trade_query(self) -> None:
        """
        解析普通成交查询
        """
        trade_reqlist = self._get_request_list("pb", "rpc.trader.stock", "query_trade")
        
        for key in trade_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_trade_dict.keys():
                self.query_trade_dict[fund] = {}
            
            if "error" not in response.keys():
                result = response["result"]["trades"]
                self.query_trade_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                self.query_trade_dict[fund][f"{rsp_time}|{key}"] = result
    
    def _parse_rzrq_trade_query(self) -> None:
        """
        解析信用成交查询
        """
        trade_reqlist = self._get_request_list("json_funid", "stockrzrq", "500014")
        
        for key in trade_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_rzrq_trade_dict.keys():
                self.query_rzrq_trade_dict[fund] = {}
            
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    # 适配一下有Array返回 但是结果为None的情况
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_rzrq_trade_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "rzrq"
                self.query_rzrq_trade_dict[fund][f"{rsp_time}|{key}"] = result
    
    def _parse_ggt_trade_query(self) -> None:
        """
        解析港股通成交查询
        """
        trade_reqlist = self._get_request_list("json_funid", "stockths", "610007")
        
        for key in trade_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_ggt_trade_dict.keys():
                self.query_ggt_trade_dict[fund] = {}
            
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    # 适配一下有Array返回 但是结果为None的情况
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_ggt_trade_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "ggt"
                self.query_ggt_trade_dict[fund][f"{rsp_time}|{key}"] = result
    
    def _get_request_list(self, protocol: str, servicename: str, cmd: str) -> List[str]:
        """
        获取请求列表
        
        Args:
            protocol: 协议类型
            servicename: 服务名称
            cmd: 命令
            
        Returns:
            请求ID列表
        """
        request_statics = self.state.request_statics
        if protocol in request_statics.keys():
            if servicename in request_statics[protocol].keys():
                if cmd in request_statics[protocol][servicename].keys():
                    return [d["key"] for d in request_statics[protocol][servicename][cmd]]
                else:
                    return []
            else:
                return []
        else:
            return []
    
    def _get_fund_by_fund_token(self, fund_token: str) -> str:
        """
        根据fund_token获取账户名称
        
        Args:
            fund_token: 资金令牌
            
        Returns:
            账户名称
        """
        if fund_token in self.state.fundtoken_dict.keys():
            return self.state.fundtoken_dict[fund_token]
        else:
            return fund_token
    
    def handle_trade_query(self) -> List[str]:
        """
        处理成交查询
        
        Returns:
            成交查询结果列表
        """
        fundlist = []
        
        # 普通成交查询
        for fund, querytimedata in self.query_trade_dict.items():
            fundlist.append(f"{fund}|normal|{len(querytimedata)}")
        
        # 信用成交查询
        for fund, querytimedata in self.query_rzrq_trade_dict.items():
            fundlist.append(f"{fund}|rzrq|{len(querytimedata)}")
        
        # 港股通成交查询
        for fund, querytimedata in self.query_ggt_trade_dict.items():
            fundlist.append(f"{fund}|ggt|{len(querytimedata)}")
        
        return fundlist
    
    def get_trade_querytime(self, fundkey: str) -> List[str]:
        """
        获取成交查询时间列表
        
        Args:
            fundkey: 资金账户键值
            
        Returns:
            查询时间列表
        """
        fund = fundkey.split("|")[0]
        querytype = fundkey.split("|")[1]
        self.trade_querytime_reqid = {}
        
        typequerydict = {
            "normal": self.query_trade_dict,
            "rzrq": self.query_rzrq_trade_dict,
            "ggt": self.query_ggt_trade_dict,
        }
        
        querydatadict = typequerydict[querytype][fund]
        querytime_list = []
        
        for key, querydata in querydatadict.items():
            querytime = key.split("|")[0]
            reqid = key.split("|")[1]
            self.trade_querytime_reqid[querytime] = reqid
            if isinstance(querydata, dict):
                querytime_list.append(f"{querytime}|-1")
            else:
                querytime_list.append(f"{querytime}|{len(querydata)}")
        
        sorted_querytime_list = [
            item for item in sorted(
                querytime_list, 
                key=lambda item: datetime.strptime(item.split('|')[0], '%Y%m%d %H:%M:%S.%f'), 
                reverse=True
            )
        ]
        return sorted_querytime_list

    def get_trade_query_data(self) -> Dict[str, Dict[str, Dict[str, pd.DataFrame]]]:
        """
        获取成交查询数据
        
        Returns:
            成交查询数据字典
        """
        typecolumn = {
            "normal": ['trade_time', 'order_no', 'symbol', 'symbol_name', 'market_name', 'price', 'quantity', 'trade_amount', 
                'order_type_msg', 'operation_msg', 'currency', 'currency_msg', "shareholder_account", 'message'],
            "rzrq": ['TransactTime', 'MarketName', 'Symbol', 'SecurityID', 'Price', 'OperationMsg', 'Side', 'AvgPx', 'BusinessAmount', 
                'GrossTradeAmt', 'OrderID', 'OrdType', 'TradeVolume', 'OrderStatus', 'OperationMsg', 'Distribution'],
            "ggt": ['TransactTime', 'MarketName', 'SecurityID', 'SecurityName', 'Price', 'OperationMsg', 'Side', 'AvgPx', 
                'BusinessAmount', 'GrossTradeAmt', 'OrderID', 'OrdType', 'TradeVolume', 'TradeStatus', 'Distribution'],
        }
        
        typecolumnrename = {
            "normal": {"symbol": "SecurityID", "symbol_name": "Symbol", "trade_amount": "trade", "order_type_msg": "type", 
                "operation_msg": "op", "market_name": "market", "currency_msg": "currency2", "shareholder_account": "gdzh"},
            "rzrq": {},
            "ggt": {"SecurityName": "Symbol"},
        }
        
        all_data_dict = {
            'normal': {},
            'rzrq': {},
            'ggt': {},
        }

        # 处理普通成交查询数据
        for fundtoken, time_dict in self.query_trade_dict.items():
            for timestamp, value in time_dict.items():
                if isinstance(value, list):
                    data = pd.DataFrame(value, columns=typecolumn['normal']).dropna(axis=1, how='all').fillna('')
                    data.rename(columns=typecolumnrename['normal'], inplace=True)
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = data if len(value) else pd.DataFrame()
                elif isinstance(value, dict):
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame([value])
                elif value == '':
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame()
        
        # 处理信用成交查询数据
        for fundtoken, time_dict in self.query_rzrq_trade_dict.items():
            for timestamp, value in time_dict.items():
                if isinstance(value, list):
                    data = pd.DataFrame(value, columns=typecolumn['rzrq']).dropna(axis=1, how='all').fillna('')
                    data.rename(columns=typecolumnrename['rzrq'], inplace=True)
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = data if len(value) else pd.DataFrame()
                elif isinstance(value, dict):
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame([value])
                elif value == '':
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame()
        
        # 处理港股通成交查询数据
        for fundtoken, time_dict in self.query_ggt_trade_dict.items():
            for timestamp, value in time_dict.items():
                if isinstance(value, list):
                    data = pd.DataFrame(value, columns=typecolumn['ggt']).dropna(axis=1, how='all').fillna('')
                    data.rename(columns=typecolumnrename['ggt'], inplace=True)
                    all_data_dict['ggt'].setdefault(fundtoken, {})[timestamp] = data if len(value) else pd.DataFrame()
                elif isinstance(value, dict):
                    all_data_dict['ggt'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame([value])
                elif value == '':
                    all_data_dict['ggt'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame()
        
        return all_data_dict
    
    def get_trade_summary(self) -> Dict[str, Any]:
        """
        获取成交查询汇总信息
        
        Returns:
            成交查询汇总字典
        """
        total_normal = sum(len(time_dict) for time_dict in self.query_trade_dict.values())
        total_rzrq = sum(len(time_dict) for time_dict in self.query_rzrq_trade_dict.values())
        total_ggt = sum(len(time_dict) for time_dict in self.query_ggt_trade_dict.values())
        
        return {
            "normal_accounts": len(self.query_trade_dict),
            "rzrq_accounts": len(self.query_rzrq_trade_dict),
            "ggt_accounts": len(self.query_ggt_trade_dict),
            "total_normal_queries": total_normal,
            "total_rzrq_queries": total_rzrq,
            "total_ggt_queries": total_ggt,
            "all_accounts": list(set(
                list(self.query_trade_dict.keys()) +
                list(self.query_rzrq_trade_dict.keys()) +
                list(self.query_ggt_trade_dict.keys())
            ))
        }
    
    def show_trade_summary(self) -> None:
        """
        显示成交查询汇总信息
        """
        summary = self.get_trade_summary()
        
        print("\n=== 成交查询汇总 ===")
        print(f"普通账户数: {summary['normal_accounts']}")
        print(f"信用账户数: {summary['rzrq_accounts']}")
        print(f"港股通账户数: {summary['ggt_accounts']}")
        print(f"普通查询总数: {summary['total_normal_queries']}")
        print(f"信用查询总数: {summary['total_rzrq_queries']}")
        print(f"港股通查询总数: {summary['total_ggt_queries']}")
        print(f"所有账户: {summary['all_accounts']}")
        print("=" * 30) 
