"""
资金查询处理器模块
负责资金账户查询和处理
"""

from typing import Dict, List, Any, Optional
import pandas as pd

from .models import FundQueryResult, ProcessingState, RequestPairsDict


class FundProcessor:
    """资金查询处理器类"""
    
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict):
        self.state = state
        self.req_pairs = req_pairs
        
        # 资金查询数据存储
        self.query_account_asset_dict = {}
        self.query_rzrq_account_asset_dict = {}
        self.query_ggt_account_asset_dict = {}
        self.query_asset_failed_list = []
    
    def parse_fund_query(self) -> None:
        """
        解析资金查询数据
        """
        # 普通资金查询
        self._parse_normal_fund_query()
        
        # 信用资金查询
        self._parse_rzrq_fund_query()
        
        # 港股通资金查询
        self._parse_ggt_fund_query()
    
    def _parse_normal_fund_query(self) -> None:
        """
        解析普通资金查询
        """
        fund_reqlist = self._get_request_list("pb", "rpc.trader.stock", "query_account_asset")
        
        for key in fund_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_account_asset_dict.keys():
                self.query_account_asset_dict[fund] = []
            
            if "error" not in response.keys():
                result = response["result"]["account_asset"][0]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                self.query_account_asset_dict[fund].append(result)
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                self.query_asset_failed_list.append(result)
    
    def _parse_rzrq_fund_query(self) -> None:
        """
        解析信用资金查询
        """
        rzrq_reqlist = self._get_request_list("json_funid", "stockrzrq", "501001")
        
        for key in rzrq_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_rzrq_account_asset_dict.keys():
                self.query_rzrq_account_asset_dict[fund] = []
            
            if "error" not in response.keys():
                result = response["result"]["Array"][0]
                result["fund_token"] = fund_token
                result["rsp_time"] = rsp_time
                result["fund"] = fund
                self.query_rzrq_account_asset_dict[fund].append(result)
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "rzrq"
                self.query_asset_failed_list.append(result)
    
    def _parse_ggt_fund_query(self) -> None:
        """
        解析港股通资金查询
        """
        ggt_reqlist = self._get_request_list("json_funid", "stockths", "610013")
        
        for key in ggt_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_ggt_account_asset_dict.keys():
                self.query_ggt_account_asset_dict[fund] = []
            
            if "Array" in response["result"].keys():
                result = response["result"]["Array"][0]
                result["fund_token"] = fund_token
                result["rsp_time"] = rsp_time
                result["fund"] = fund
                self.query_ggt_account_asset_dict[fund].append(result)
            else:
                result = {
                    "type": "ggt",
                    "rsp_time": rsp_time,
                    "fund": fund,
                    "req_id": key,
                    "code": -1,
                    "message": "未返回资金查询结果"
                }
                self.query_asset_failed_list.append(result)
    
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
    
    def handle_fund_query(self) -> List[str]:
        """
        处理资金查询
        
        Returns:
            资金查询结果列表
        """
        fund_list = []
        
        # 普通资金查询
        for key, item in self.query_account_asset_dict.items():
            fund_list.append(f'{key}|normal|{len(item)}')
        
        # 信用资金查询
        for key, item in self.query_rzrq_account_asset_dict.items():
            fund_list.append(f'{key}|rzrq|{len(item)}')
        
        # 港股通资金查询
        for key, item in self.query_ggt_account_asset_dict.items():
            fund_list.append(f'{key}|ggt|{len(item)}')
        
        return fund_list
    
    def get_fund_query_data(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        获取资金查询数据
        
        Returns:
            资金查询数据字典
        """
        columns_query_type_dict = {
            "normal": ["rsp_time", "available_value", "balance_value", "currency_msg",
                      "frozen_value", "market_value", "total_assets", "total_net_value"],
            "rzrq": ["rsp_time", "EnableBalance", "AvailableValue", "AvailableMargin",
                    "FinEnableQuota", "SloEnableQuota", "FinCompactalance", "SloCompactBalance",
                    "FundAsset", "TotalAssets", "NetMoney", "WT_ZJ_JZC"],
            "ggt": ["rsp_time", "TotalAssets", "AvailableValue", "GGT_SRZS", "GGT_ZTCZ", "GGT_ZTRZ",
                   "GGT_SSCZ", "GGT_SSRZ", "GGT_YSCZZJ", "GGT_HCJE", "GGT_HRJE", "GGT_SYJE", "GGT_ZJKM", "GGT_SSZYJE"],
            "failed": ["rsp_time", "fund", "req_id", "code", "message"],
        }
        
        all_data_dict = {
            'normal': {},
            'rzrq': {},
            'ggt': {},
            'failed': {}
        }

        # 处理普通资金查询数据
        for key, value in self.query_account_asset_dict.items():
            all_data_dict['normal'][key] = pd.DataFrame(value, columns=columns_query_type_dict['normal']) if len(value) else pd.DataFrame()
        
        # 处理信用资金查询数据
        for key, value in self.query_rzrq_account_asset_dict.items():
            all_data_dict['rzrq'][key] = pd.DataFrame(value, columns=columns_query_type_dict['rzrq']) if len(value) else pd.DataFrame()
        
        # 处理港股通资金查询数据
        for key, value in self.query_ggt_account_asset_dict.items():
            all_data_dict['ggt'][key] = pd.DataFrame(value, columns=columns_query_type_dict['ggt']) if len(value) else pd.DataFrame()
        
        # 处理失败查询数据
        all_data_dict['failed']['all'] = pd.DataFrame(self.query_asset_failed_list, columns=columns_query_type_dict['failed']) if self.query_asset_failed_list else pd.DataFrame()
        
        return all_data_dict
    
    def get_fund_summary(self) -> Dict[str, Any]:
        """
        获取资金查询汇总信息
        
        Returns:
            资金查询汇总字典
        """
        total_normal = sum(len(items) for items in self.query_account_asset_dict.values())
        total_rzrq = sum(len(items) for items in self.query_rzrq_account_asset_dict.values())
        total_ggt = sum(len(items) for items in self.query_ggt_account_asset_dict.values())
        
        return {
            "normal_accounts": len(self.query_account_asset_dict),
            "rzrq_accounts": len(self.query_rzrq_account_asset_dict),
            "ggt_accounts": len(self.query_ggt_account_asset_dict),
            "total_normal_queries": total_normal,
            "total_rzrq_queries": total_rzrq,
            "total_ggt_queries": total_ggt,
            "failed_queries": len(self.query_asset_failed_list),
            "all_accounts": list(set(
                list(self.query_account_asset_dict.keys()) +
                list(self.query_rzrq_account_asset_dict.keys()) +
                list(self.query_ggt_account_asset_dict.keys())
            ))
        }
    
    def show_fund_summary(self) -> None:
        """
        显示资金查询汇总信息
        """
        summary = self.get_fund_summary()
        
        print("\n=== 资金查询汇总 ===")
        print(f"普通账户数: {summary['normal_accounts']}")
        print(f"信用账户数: {summary['rzrq_accounts']}")
        print(f"港股通账户数: {summary['ggt_accounts']}")
        print(f"普通查询总数: {summary['total_normal_queries']}")
        print(f"信用查询总数: {summary['total_rzrq_queries']}")
        print(f"港股通查询总数: {summary['total_ggt_queries']}")
        print(f"失败查询数: {summary['failed_queries']}")
        print(f"所有账户: {summary['all_accounts']}")
        print("=" * 30) 
