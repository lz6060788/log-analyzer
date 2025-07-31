"""
融资融券处理器模块
负责融资融券相关的日志解析、数据处理与展示
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from .models import ProcessingState, RequestPairsDict

class FinancingProcessor:
    """
    融资融券处理器类
    """
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict):
        self.state = state
        self.req_pairs = req_pairs
        # 可融资标的券
        self.finable_security_dict: Dict[str, Dict[str, Any]] = {}
        self.finable_querytime_reqid: Dict[str, str] = {}
        self.finable_security_failed: List[Dict[str, Any]] = []

    def parse_financing_query(self) -> None:
        """
        解析可融资标的券相关数据
        """
        self.finable_security_dict = {}
        self.finable_querytime_reqid = {}
        self.finable_security_failed = []
        rzrq_reqlist = self._get_request_list("json_funid", "stockrzrq", "501005")
        for key in rzrq_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self._get_fund_by_fund_token(fund_token)
            if fund not in self.finable_security_dict:
                self.finable_security_dict[fund] = {}
            if "error" not in response:
                if "Array" in response["result"]:
                    result = response["result"]["Array"]
                    self.finable_querytime_reqid[rsp_time] = key
                    self.finable_security_dict[fund][f"{rsp_time}|{len(result)}"] = result
                else:
                    self.finable_security_failed.append({
                        "fund": fund,
                        "rsp_time": rsp_time,
                        "req_id": key,
                        "message": "result返回结果中没有Array",
                    })
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                self.finable_security_failed.append(result)

    def _get_request_list(self, protocol: str, servicename: str, cmd: str) -> List[str]:
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
        return self.state.fundtoken_dict.get(fund_token, fund_token)

    def handle_finable_security_query(self) -> List[str]:
        """
        汇总可融资标的券的资金账户列表
        """
        fund_list = list(self.finable_security_dict.keys())
        return fund_list

    def get_finable_security_querytime(self, fundkey: str) -> List[str]:
        """
        获取指定资金账户的可融资标的券查询时间列表
        """
        querydatadict = self.finable_security_dict.get(fundkey, {})
        querytime_list = list(querydatadict.keys())
        # 按时间倒序排列
        sorted_querytime_list = sorted(querytime_list, key=lambda item: item.split('|')[0], reverse=True)
        if not sorted_querytime_list:
            sorted_querytime_list.append("空")
        return sorted_querytime_list 

    # Jupyter友好型接口
    def show_finable_security(self, fund_key: str, query_time: str, show_securities: bool = False, stock_code: str = "") -> None:
        """
        展示可融资标的券信息（Jupyter友好）
        """
        if query_time != "空":
            querytime = query_time.split('|')[0]
            reqid = self.finable_querytime_reqid.get(querytime, "")
            print("查询账户", fund_key)
            print("查询时间", querytime)
            print("req_id", reqid, '\n')
            if stock_code == "":
                query_data = self.finable_security_dict[fund_key][query_time]
                market_dict = {}
                for data in query_data:
                    market = data.get("MarketID", "")
                    security = data.get("SecurityID", "")
                    market_name = data.get("MarketName", "")
                    index = f'{market_name}:{market}'
                    if index not in market_dict:
                        market_dict[index] = []
                    market_dict[index].append(security)
                for index, security_list in market_dict.items():
                    print(index, "股票数：" + str(len(security_list)))
                    if show_securities:
                        print(security_list)
            else:
                is_finded = False
                query_data = self.finable_security_dict[fund_key][query_time]
                for data in query_data:
                    market = data.get("MarketID", "")
                    security = data.get("SecurityID", "")
                    if security == stock_code:
                        display(pd.DataFrame([data]))
                        is_finded = True
                if not is_finded:
                    print(f"证券代码 {stock_code} 不在可融资股票列表之中")
        df = pd.DataFrame(self.finable_security_failed, columns=["rsp_time", "fund", "req_id", "code", "message"])
        df = df[df["fund"] == fund_key]
        print("\n失败查询请求", fund_key)
        display(df)

    # Web友好型接口
    def get_finable_security_data(self, fund_key: Optional[str] = None) -> Dict[str, Any]:
        """
        获取可融资标的券数据（Web友好）
        """
        if fund_key:
            return self.finable_security_dict.get(fund_key, {})
        return self.finable_security_dict

    def get_finable_security_failed(self) -> List[Dict[str, Any]]:
        """
        获取失败的可融资标的券查询（Web友好）
        """
        return self.finable_security_failed
