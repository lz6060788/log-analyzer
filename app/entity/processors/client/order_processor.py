"""
委托查询处理器模块
负责委托订单查询和处理
"""

import json
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from .models import OrderQueryResult, ProcessingState, RequestPairsDict


class OrderProcessor:
    """委托查询处理器类"""
    
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict):
        self.state = state
        self.req_pairs = req_pairs
        
        # 委托查询数据存储
        self.query_order_dict = {}
        self.query_rzrq_order_dict = {}
        self.query_ggt_order_dict = {}
        self.query_order_df = {}
        self.order_querytime_reqid = {}
    
    def parse_order_query(self) -> None:
        """
        解析委托查询数据
        """
        # 普通委托查询
        self._parse_normal_order_query()
        
        # 信用委托查询
        self._parse_rzrq_order_query()
        
        # 港股通委托查询
        self._parse_ggt_order_query()
    
    def _parse_normal_order_query(self) -> None:
        """
        解析普通委托查询
        """
        order_reqlist = self._get_request_list("pb", "rpc.trader.stock", "query_order")
        
        for key in order_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_order_dict.keys():
                self.query_order_dict[fund] = {}
            
            if "error" not in response.keys():
                result = response["result"]["orders"]
                self.query_order_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                # 这里可以添加失败处理逻辑
        
        # 适配调用500013查普通委托的情况
        order_reqlist = self._get_request_list("json_funid", "stockths", "500013")
        
        for key in order_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["UserToken"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_order_dict.keys():
                self.query_order_dict[fund] = {}
            
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_order_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                # 这里可以添加失败处理逻辑
    
    def _parse_rzrq_order_query(self) -> None:
        """
        解析信用委托查询
        """
        order_reqlist = self._get_request_list("json_funid", "stockrzrq", "500013")
        
        for key in order_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_rzrq_order_dict.keys():
                self.query_rzrq_order_dict[fund] = {}
            
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_rzrq_order_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "rzrq"
                # 这里可以添加失败处理逻辑
    
    def _parse_ggt_order_query(self) -> None:
        """
        解析港股通委托查询
        """
        order_reqlist = self._get_request_list("json_funid", "stockths", "610005")
        
        for key in order_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            
            if fund not in self.query_ggt_order_dict.keys():
                self.query_ggt_order_dict[fund] = {}
            
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_ggt_order_dict[fund][f"{rsp_time}|{key}"] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "ggt"
                # 这里可以添加失败处理逻辑
    
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
    
    def handle_order_query(self) -> List[str]:
        """
        处理委托查询
        
        Returns:
            委托查询结果列表
        """
        fundlist = []
        
        # 普通委托查询
        for fund, querytimedata in self.query_order_dict.items():
            fundlist.append(f"{fund}|normal|{len(querytimedata)}")
        
        # 信用委托查询
        for fund, querytimedata in self.query_rzrq_order_dict.items():
            fundlist.append(f"{fund}|rzrq|{len(querytimedata)}")
        
        # 港股通委托查询
        for fund, querytimedata in self.query_ggt_order_dict.items():
            fundlist.append(f"{fund}|ggt|{len(querytimedata)}")
        
        return fundlist
    
    def get_order_querytime(self, fundkey: str) -> List[str]:
        """
        获取委托查询时间列表
        
        Args:
            fundkey: 资金账户键值
            
        Returns:
            查询时间列表
        """
        fund = fundkey.split("|")[0]
        querytype = fundkey.split("|")[1]
        self.order_querytime_reqid = {}
        
        typequerydict = {
            "normal": self.query_order_dict,
            "rzrq": self.query_rzrq_order_dict,
            "ggt": self.query_ggt_order_dict,
        }
        
        querydatadict = typequerydict[querytype][fund]
        querytime_list = []
        
        for key, querydata in querydatadict.items():
            querytime = key.split("|")[0]
            reqid = key.split("|")[1]
            self.order_querytime_reqid[querytime] = reqid
            querytime_list.append(f"{querytime}|{len(querydata)}")
        
        sorted_querytime_list = [
            item for item in sorted(
                querytime_list, 
                key=lambda item: datetime.strptime(item.split('|')[0], '%Y%m%d %H:%M:%S.%f'), 
                reverse=True
            )
        ]
        return sorted_querytime_list
    
    def show_queryorder(self, account: str, querytime: str) -> None:
        """
        显示委托查询结果
        
        Args:
            account: 账户信息
            querytime: 查询时间
        """
        fund = account.split("|")[0]
        querytype = account.split("|")[1]
        cnt = int(querytime.split("|")[1])
        querytime_str = querytime.split("|")[0]
        reqid = self.order_querytime_reqid[querytime_str]
        
        typequerydict = {
            "normal": self.query_order_dict,
            "rzrq": self.query_rzrq_order_dict,
            "ggt": self.query_ggt_order_dict,
        }
        
        typecolumn = {
            "normal": ['insert_time', 'symbol', 'symbol_name', 'market_name', 'operation_msg', 'price', 'AvgPx', 'quantity', 'trade_amount', 
                'avg_price', 'order_no', 'order_status_msg', 'order_type_msg', 'currency', 'message',
                'OrderEntryTime', 'MarketName', 'Symbol', 'SecurityID', 'Price', 'OrderQty', 'Side', 'AvgPx', 'TradeVolume', 
                'OrderID', 'OperationMsg', 'Distribution', 'OrderStatusMsg', 'OrdType', 'OrderStatus2946'],
            "rzrq": ['OrderEntryTime', 'MarketName', 'Symbol', 'SecurityID', 'Price', 'OrderQty', 'Side', 'AvgPx', 'TradeVolume', 
                'OrderID', 'OperationMsg', 'Distribution', 'OrderStatusMsg', 'OrdType', 'OrderStatus2946'],
            "ggt": ['OrderTime', 'Market', 'MarketName', 'SecurityID', 'SecurityName', 'OrderPrice', 'OrderQty', 'Side', 'AvgPx',
                'TradeVolume', 'OrderID', 'OperationMsg', 'OrderStatusMsg'],
        }
        
        typecolumnrename = {
            "normal": {"symbol": "security", "symbol_name": "symbol", "trade_amount": "trade", "order_status_msg": "status",
                "order_type_msg": "type", "avg_price": "avg", "operation_msg": "op", "market_name": "market"},
            "rzrq": {},
            "ggt": {"SecurityID": "Security", "SecurityName": "Symbol", "OrderPrice": "Price", "TradeVolume": "Volume"},
        }
        
        print(f"fund: {fund}")
        print(f"querytype: {querytype}")
        print(f"req_id: {reqid}")
        
        if cnt == 0:
            print("本次委托查询结果为空")
        else:
            querydata = typequerydict[querytype][fund][f"{querytime_str}|{reqid}"]
            df_queryorder = pd.DataFrame(querydata, columns=typecolumn[querytype])
            df_queryorder.rename(columns=typecolumnrename[querytype], inplace=True)
            df_queryorder = df_queryorder.dropna(axis=1, how='all')
            
            if not df_queryorder.empty:
                print(df_queryorder)
    
    def get_order_query_data(self) -> Dict[str, Dict[str, Dict[str, pd.DataFrame]]]:
        """
        获取委托查询数据
        
        Returns:
            委托查询数据字典
        """
        typecolumn = {
            "normal": ['insert_time', 'symbol', 'symbol_name', 'market_name', 'operation_msg', 'price', 'AvgPx', 'quantity', 'trade_amount', 
                'avg_price', 'order_no', 'order_status_msg', 'order_type_msg', 'currency', 'message',
                'OrderEntryTime', 'MarketName', 'Symbol', 'SecurityID', 'Price', 'OrderQty', 'Side', 'AvgPx', 'TradeVolume', 
                'OrderID', 'OperationMsg', 'Distribution', 'OrderStatusMsg', 'OrdType', 'OrderStatus2946'],
            "rzrq": ['OrderEntryTime', 'MarketName', 'Symbol', 'SecurityID', 'Price', 'OrderQty', 'Side', 'AvgPx', 'TradeVolume', 
                'OrderID', 'OperationMsg', 'Distribution', 'OrderStatusMsg', 'OrdType', 'OrderStatus2946'],
            "ggt": ['OrderTime', 'Market', 'MarketName', 'SecurityID', 'SecurityName', 'OrderPrice', 'OrderQty', 'Side', 'AvgPx',
                'TradeVolume', 'OrderID', 'OperationMsg', 'OrderStatusMsg'],
        }
        
        typecolumnrename = {
            "normal": {"symbol": "security", "symbol_name": "symbol", "trade_amount": "trade", "order_status_msg": "status",
                "order_type_msg": "type", "avg_price": "avg", "operation_msg": "op", "market_name": "market"},
            "rzrq": {},
            "ggt": {"SecurityID": "Security", "SecurityName": "Symbol", "OrderPrice": "Price", "TradeVolume": "Volume"},
        }
        
        all_data_dict = {
            'normal': {},
            'rzrq': {},
            'ggt': {},
        }

        # 处理普通委托查询数据
        for fundtoken, time_dict in self.query_order_dict.items():
            for timestamp, value in time_dict.items():
                if isinstance(value, list):
                    data = pd.DataFrame(value, columns=typecolumn['normal']).dropna(axis=1, how='all').fillna('')
                    data.rename(columns=typecolumnrename['normal'], inplace=True)
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = data if len(value) else pd.DataFrame()
                elif isinstance(value, dict):
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame([value])
                elif value == '':
                    all_data_dict['normal'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame()
        
        # 处理信用委托查询数据
        for fundtoken, time_dict in self.query_rzrq_order_dict.items():
            for timestamp, value in time_dict.items():
                if isinstance(value, list):
                    data = pd.DataFrame(value, columns=typecolumn['rzrq']).dropna(axis=1, how='all').fillna('')
                    data.rename(columns=typecolumnrename['rzrq'], inplace=True)
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = data if len(value) else pd.DataFrame()
                elif isinstance(value, dict):
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame([value])
                elif value == '':
                    all_data_dict['rzrq'].setdefault(fundtoken, {})[timestamp] = pd.DataFrame()
        
        # 处理港股通委托查询数据
        for fundtoken, time_dict in self.query_ggt_order_dict.items():
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
    
    def show_queryorder_summary(self, account):
        fund = account.split("|")[0]
        querytype = account.split("|")[1]
        typequerydict = {
            "normal":self.query_order_dict,
            "rzrq":self.query_rzrq_order_dict,
            "ggt":self.query_ggt_order_dict,
        }
        print("\n统计单账户查询请求返回行数")
        print("查询账号：", account, '\n')
        for query_time, querydata in typequerydict[querytype][fund].items():
            print(query_time, len(querydata))

    def get_order_summary(self) -> Dict[str, Any]:
        """
        获取委托查询汇总信息
        
        Returns:
            委托查询汇总字典
        """
        total_normal = sum(len(time_dict) for time_dict in self.query_order_dict.values())
        total_rzrq = sum(len(time_dict) for time_dict in self.query_rzrq_order_dict.values())
        total_ggt = sum(len(time_dict) for time_dict in self.query_ggt_order_dict.values())
        
        return {
            "normal_accounts": len(self.query_order_dict),
            "rzrq_accounts": len(self.query_rzrq_order_dict),
            "ggt_accounts": len(self.query_ggt_order_dict),
            "total_normal_queries": total_normal,
            "total_rzrq_queries": total_rzrq,
            "total_ggt_queries": total_ggt,
            "all_accounts": list(set(
                list(self.query_order_dict.keys()) +
                list(self.query_rzrq_order_dict.keys()) +
                list(self.query_ggt_order_dict.keys())
            ))
        }
    
    def show_order_summary(self) -> None:
        """
        显示委托查询汇总信息
        """
        summary = self.get_order_summary()
        
        print("\n=== 委托查询汇总 ===")
        print(f"普通账户数: {summary['normal_accounts']}")
        print(f"信用账户数: {summary['rzrq_accounts']}")
        print(f"港股通账户数: {summary['ggt_accounts']}")
        print(f"普通查询总数: {summary['total_normal_queries']}")
        print(f"信用查询总数: {summary['total_rzrq_queries']}")
        print(f"港股通查询总数: {summary['total_ggt_queries']}")
        print(f"所有账户: {summary['all_accounts']}")
        print("=" * 30) 

    def show_queryorder_all(self):
        # 按时间戳统计查询条数
        print("\n根据时间统计查询行数\n")
        column_index = set()
        row_index = set()
        typequerydict = {
            "normal":self.query_order_dict,
            "rzrq":self.query_rzrq_order_dict,
            "ggt":self.query_ggt_order_dict,
        }
        for querytype, querydict in typequerydict.items():
            for fundkey, fundquerydata in querydict.items():
                for timekey, querydata in fundquerydata.items():
                    timestamp = timekey.split(' ')[1].split('.')[0]
                    column_index.add("%s|%s" % (fundkey, querytype))
                    row_index.add(timestamp)
        column_index = list(column_index)
        row_index = sorted(list(row_index))
        
        df = pd.DataFrame(index=row_index, columns=column_index)
        for querytype, querydict in typequerydict.items():
            for fundkey, fundquerydata in querydict.items():
                for timekey, querydata in fundquerydata.items():
                    timestamp = timekey.split(' ')[1].split('.')[0]
                    df.loc[timestamp, "%s|%s" % (fundkey, querytype)] = len(querydata)
        df = df.fillna(0)
        df = df.loc[:, (df != 0).any(axis=0)]
        df['total'] = df.sum(axis=1)
        cols = df.columns.tolist()
        cols = cols[-1:] + cols[:-1]  # 将 'total' 列移到最前面
        df = df[cols]
        display(df)
