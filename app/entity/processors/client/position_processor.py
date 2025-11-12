"""
持仓查询处理器模块
负责持仓信息查询和处理
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from .models import PositionQueryResult, ProcessingState, RequestPairsDict


class PositionProcessor:
    """持仓查询处理器类"""
    
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict):
        self.state = state
        self.req_pairs = req_pairs
        
        # 持仓查询数据存储
        self.query_account_stock_dict = {}
        self.query_rzrq_account_stock_dict = {}
        self.query_ggt_account_stock_dict = {}
        self.query_stock_failed_list = []
        self.position_querytime_reqid = {}
    
    def parse_position_query(self) -> None:
        """
        解析持仓查询数据
        """
        # 普通持仓查询
        self._parse_normal_position_query()
        
        # 信用持仓查询
        self._parse_rzrq_position_query()
        
        # 港股通持仓查询
        self._parse_ggt_position_query()
    
    def _parse_normal_position_query(self) -> None:
        """
        解析普通持仓查询
        """
        position_reqlist = self._get_request_list("pb", "rpc.trader.stock", "query_account_stock")
        
        for key in position_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_account_stock_dict.keys():
                self.query_account_stock_dict[fund] = {}
            
            if "error" not in response.keys():
                result = response["result"]["account_stock"]
                self.query_account_stock_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                self.query_stock_failed_list.append(result)
    
    def _parse_rzrq_position_query(self) -> None:
        """
        解析信用持仓查询
        """
        position_reqlist = self._get_request_list("json_funid", "stockrzrq", "501002")
        
        for key in position_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_rzrq_account_stock_dict.keys():
                self.query_rzrq_account_stock_dict[fund] = {}
            
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    result = response["result"]["Array"]
                self.query_rzrq_account_stock_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "rzrq"
                self.query_stock_failed_list.append(result)
    
    def _parse_ggt_position_query(self) -> None:
        """
        解析港股通持仓查询
        """
        position_reqlist = self._get_request_list("json_funid", "stockths", "610004")
        
        for key in position_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_ggt_account_stock_dict.keys():
                self.query_ggt_account_stock_dict[fund] = {}
            
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    result = response["result"]["Array"]
                self.query_ggt_account_stock_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "ggt"
                self.query_stock_failed_list.append(result)
    
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
    
    def handle_position_query(self) -> List[str]:
        """
        处理持仓查询
        
        Returns:
            持仓查询结果列表
        """
        fundlist = []
        
        # 普通持仓查询
        for fund, querytimedata in self.query_account_stock_dict.items():
            fundlist.append(f"{fund}|normal|{len(querytimedata)}")
        
        # 信用持仓查询
        for fund, querytimedata in self.query_rzrq_account_stock_dict.items():
            fundlist.append(f"{fund}|rzrq|{len(querytimedata)}")
        
        # 港股通持仓查询
        for fund, querytimedata in self.query_ggt_account_stock_dict.items():
            fundlist.append(f"{fund}|ggt|{len(querytimedata)}")
        
        return fundlist
    
    def get_position_querytime(self, fundkey: str) -> List[str]:
        """
        获取持仓查询时间列表
        
        Args:
            fundkey: 资金账户键值
            
        Returns:
            查询时间列表
        """
        fund = fundkey.split("|")[0]
        querytype = fundkey.split("|")[1]
        self.position_querytime_reqid = {}
        
        typequerydict = {
            "normal": self.query_account_stock_dict,
            "rzrq": self.query_rzrq_account_stock_dict,
            "ggt": self.query_ggt_account_stock_dict,
        }
        
        querydatadict = typequerydict[querytype][fund]
        querytime_list = []
        
        for key, querydata in querydatadict.items():
            querytime = key.split("|")[0]
            reqid = key.split("|")[1]
            self.position_querytime_reqid[querytime] = reqid
            querytime_list.append(f"{querytime}|{len(querydata)}")
        
        sorted_querytime_list = [
            item for item in sorted(
                querytime_list, 
                key=lambda item: datetime.strptime(item.split('|')[0], '%Y%m%d %H:%M:%S.%f'), 
                reverse=True
            )
        ]
        return sorted_querytime_list
    def get_position_query_data(self) -> Dict[str, Dict[str, Dict[str, pd.DataFrame]]]:
        """
        获取持仓查询数据
        
        Returns:
            持仓查询数据字典
        """
        typecolumn = {
            "normal": ['security_id', 'security_name', 'actual_amt', 'available_purchase_amt', 'available_stock_balance',
                'cost_price', 'frozen_qty', 'market', 'market_name', 'market_price', 'market_value', 'stock_balance', 'yield'],
            "rzrq": ['SecurityID', 'SecurityName', 'AccountSecPosition', 'AvailableAmt', 'CostPrice', 'FrozenAmt', "Market",
                'MarketName', 'MarketPrice', 'MarketValue', 'StockBalance', 'Yield'],
            "ggt": ['SecurityID', 'SecurityName', 'AvailableStockBalance', 'ActualAmt', 'StockBalance', 'FrozenQty',
                'CostPrice', "Market", 'MarketName', 'MarketPrice', 'MarketValue', 'Yield'],
        }
        
        typecolumnrename = {
            "normal": {"available_purchase_amt": "avail_purch", "available_stock_balance": "avail_amt", "security_id": "security", "security_name": "symbol"},
            "rzrq": {"AccountSecPosition": "ActualAmt"},
            "ggt": {"SecurityID": "Security", "SecurityName": "Symbol", "AvailableStockBalance": "Available", "Market": "market", "MarketName": "Market"},
        }
        
        all_data_dict = {
            'normal': {},
            'rzrq': {},
            'ggt': {},
        }

        # 处理普通持仓查询数据
        for fundtoken, time_dict in self.query_account_stock_dict.items():
            for timestamp, value in time_dict.items():
                if isinstance(value, list):
                    data = pd.DataFrame(value, columns=typecolumn['normal']).dropna(axis=1, how='all').fillna('')
                    data.rename(columns=typecolumnrename['normal'], inplace=True)
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = data if len(value) else pd.DataFrame()
                elif isinstance(value, dict):
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame([value])
                elif value == '':
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame()
        
        # 处理信用持仓查询数据
        for fundtoken, time_dict in self.query_rzrq_account_stock_dict.items():
            for timestamp, value in time_dict.items():
                if isinstance(value, list):
                    data = pd.DataFrame(value, columns=typecolumn['rzrq']).dropna(axis=1, how='all').fillna('')
                    data.rename(columns=typecolumnrename['rzrq'], inplace=True)
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = data if len(value) else pd.DataFrame()
                elif isinstance(value, dict):
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame([value])
                elif value == '':
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame()
        
        # 处理港股通持仓查询数据
        for fundtoken, time_dict in self.query_ggt_account_stock_dict.items():
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
    
    def get_position_summary(self) -> Dict[str, Any]:
        """
        获取持仓查询汇总信息
        
        Returns:
            持仓查询汇总字典
        """
        total_normal = sum(len(time_dict) for time_dict in self.query_account_stock_dict.values())
        total_rzrq = sum(len(time_dict) for time_dict in self.query_rzrq_account_stock_dict.values())
        total_ggt = sum(len(time_dict) for time_dict in self.query_ggt_account_stock_dict.values())
        
        return {
            "normal_accounts": len(self.query_account_stock_dict),
            "rzrq_accounts": len(self.query_rzrq_account_stock_dict),
            "ggt_accounts": len(self.query_ggt_account_stock_dict),
            "total_normal_queries": total_normal,
            "total_rzrq_queries": total_rzrq,
            "total_ggt_queries": total_ggt,
            "failed_queries": len(self.query_stock_failed_list),
            "all_accounts": list(set(
                list(self.query_account_stock_dict.keys()) +
                list(self.query_rzrq_account_stock_dict.keys()) +
                list(self.query_ggt_account_stock_dict.keys())
            ))
        }
    
    def show_position_summary(self) -> None:
        """
        显示持仓查询汇总信息
        """
        summary = self.get_position_summary()
        
        print("\n=== 持仓查询汇总 ===")
        print(f"普通账户数: {summary['normal_accounts']}")
        print(f"信用账户数: {summary['rzrq_accounts']}")
        print(f"港股通账户数: {summary['ggt_accounts']}")
        print(f"普通查询总数: {summary['total_normal_queries']}")
        print(f"信用查询总数: {summary['total_rzrq_queries']}")
        print(f"港股通查询总数: {summary['total_ggt_queries']}")
        print(f"失败查询数: {summary['failed_queries']}")
        print(f"所有账户: {summary['all_accounts']}")
        print("=" * 30) 
