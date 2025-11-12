"""
新股申购处理器模块
负责新股申购额度与中签明细的解析与处理
"""

from typing import Dict, List, Any, Optional

from .models import ProcessingState, RequestPairsDict

class IPOProcessor:
    """新股申购处理器类"""
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict):
        self.state = state
        self.req_pairs = req_pairs
        self.ipo_query_list: List[Dict[str, Any]] = []
        self.ipo_lottery_list: List[Dict[str, Any]] = []

    def parse_ipo_query(self) -> None:
        """
        解析新股申购额度查询
        """
        self.ipo_query_list = []
        for protocol, service, funid in [
            ("json_funid", "stockths", "503002"),
            ("json_funid", "stockrzrq", "501022")
        ]:
            req_list = self._get_request_list(protocol, service, funid)
            for key in req_list:
                item = self.req_pairs[key]
                request = item["request"]
                response = item["response"]
                rsp_time = item["rsp_time"]
                fund_token = request["params"].get("UserToken", "")
                query = {
                    "rsp_time": rsp_time,
                    "req_id": key,
                    "funid": funid,
                    "fund": self._get_fund_by_fund_token(fund_token)
                }
                if "result" not in response:
                    query["message"] = response.get("error", {}).get("message", "无返回")
                else:
                    if "Array" in response["result"]:
                        querydata = response["result"]["Array"]
                        try:
                            for item in querydata:
                                market = item.get("MarketName", "")
                                marketid = str(item.get("Market", ""))
                                available = item.get("AvailableStockBalance", "")
                                marketname = f'{marketid}|{market}'
                                query[f"[{marketname}]额度"] = available
                        except Exception as e:
                            query["message"] = f"返回结果异常：{e}"
                    else:
                        query["message"] = "未返回查询结果"
                self.ipo_query_list.append(query)

    def parse_ipo_lottery_query(self) -> None:
        """
        解析新股中签明细查询
        """
        self.ipo_lottery_list = []
        for protocol, service, funid in [
            ("json_funid", "stockths", "503003"),
            ("json_funid", "stockrzrq", "501023")
        ]:
            req_list = self._get_request_list(protocol, service, funid)
            for key in req_list:
                item = self.req_pairs[key]
                request = item["request"]
                response = item["response"]
                rsp_time = item["rsp_time"]
                fund_token = request["params"].get("UserToken", "")
                query = {
                    "rsp_time": rsp_time,
                    "req_id": key,
                    "funid": funid,
                    "fund": self._get_fund_by_fund_token(fund_token)
                }
                if "result" not in response:
                    query["message"] = response.get("error", {}).get("message", "无返回")
                else:
                    if "Array" in response["result"]:
                        querydata = response["result"]["Array"]
                        try:
                            for item in querydata:
                                market = item.get("MarketName", "")
                                marketid = str(item.get("Market", ""))
                                available = item.get("AvailableStockBalance", "")
                                marketname = f'{marketid}|{market}'
                                query[f"[{marketname}]额度"] = available
                        except Exception as e:
                            query["message"] = f"返回结果异常：{e}"
                    else:
                        query["message"] = "未返回查询结果"
                self.ipo_lottery_list.append(query)

    def _get_request_list(self, protocol: str, servicename: str, cmd: str) -> List[str]:
        request_statics = self.state.request_statics
        if protocol in request_statics.keys():
            if servicename in request_statics[protocol].keys():
                if cmd in request_statics[protocol][servicename].keys():
                    return [d["key"] for d in request_statics[protocol][servicename][cmd]]
        return []

    def _get_fund_by_fund_token(self, fund_token: str) -> str:
        if fund_token in self.state.fundtoken_dict.keys():
            return self.state.fundtoken_dict[fund_token]
        else:
            return fund_token

    def handle_ipo_query(self) -> List[str]:
        """
        处理新股申购额度查询，返回账户列表
        """
        fund_list = list(set([item["fund"] for item in self.ipo_query_list]))
        fund_list.insert(0, "全部")
        return fund_list
    def handle_ipo_lottery_query(self) -> List[str]:
        """
        处理新股中签明细查询，返回账户列表
        """
        fund_list = list(set([item["fund"] for item in self.ipo_lottery_list]))
        fund_list.insert(0, "全部")
        return fund_list
    def get_ipo_query_data(self, fund: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取新股申购额度数据，适合web接口返回
        Args:
            fund: 指定账户（可选），为None时返回全部
        Returns:
            额度数据列表
        """
        if fund is None or fund == "全部":
            return self.ipo_query_list.copy()
        else:
            return [item for item in self.ipo_query_list if item["fund"] == fund]

    def get_ipo_lottery_data(self, fund: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取新股中签明细数据，适合web接口返回
        Args:
            fund: 指定账户（可选），为None时返回全部
        Returns:
            中签明细数据列表
        """
        if fund is None or fund == "全部":
            return self.ipo_lottery_list.copy()
        else:
            return [item for item in self.ipo_lottery_list if item["fund"] == fund] 
