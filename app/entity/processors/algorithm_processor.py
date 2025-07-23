"""
算法交易处理器模块
负责算法订单的解析、处理与数据输出
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime
from .models import ProcessingState, RequestPairsDict

class AlgorithmProcessor:
    """算法交易处理器类"""
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict):
        self.state = state
        self.req_pairs = req_pairs
        self.algorithm_list: List[Dict[str, Any]] = []
        self.algorithm_detail_dict: Dict[str, Dict[str, Any]] = {}
        self.algorithm_query_dict: Dict[str, List[Dict[str, Any]]] = {}
        self.query_algorithm_df: Dict[str, Any] = {}
        self.algorithm_push: Dict[str, Dict[str, Any]] = {}

    def parse_algorithm_query(self) -> None:
        """
        解析算法订单相关数据
        """
        self.algorithm_list = []
        self.algorithm_detail_dict = {}
        self.algorithm_query_dict = {}
        self.query_algorithm_df = {}
        self.algorithm_push = {}
        for key, value in self.req_pairs.items():
            protocol = value.get("protocol", "")
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            if protocol == "json":
                if request.get("method") == "new_instmanage":
                    dict_inst_type = ["普通","条件单","算法单"]
                    dict_init_desc = ["启动","暂停"]
                    dict_expire_desc = ["撤单","不撤"]
                    dict_special_desc = ["跟限价委托", "不委托"]
                    action = request["params"].get("action")
                    if action == "query" and "instructionid" not in request["params"]:
                        query_data = response["result"]["instructions"]
                        format_query_data = []
                        for item in query_data:
                            instanceid = item["instructionid"]
                            fund = ""
                            fund_token = item.get("fund_token", "")
                            if hasattr(self.state, "client_fundtoken_mapping") and fund_token in self.state.client_fundtoken_mapping:
                                mapped = self.state.client_fundtoken_mapping[fund_token]
                                if mapped in self.state.fundtoken_dict:
                                    fund = self.state.fundtoken_dict[mapped]
                            format_query_data.append({
                                "rsp_time": rsp_time,
                                "fund": fund,
                                "inst_id": instanceid,
                                "inst_type": dict_inst_type[item["instructiontype"]],
                                "algorithm": item["instructionparam"]["algorithmtype"],
                                "security": item["security"],
                                "side": item["side"],
                                "总数": item["qty"],
                                "剩余": item["qtyleft"],
                                "成交": item["qtytrade"],
                                "撤销": item["qtycancel"],
                                "状态": item["statusmsg"],
                            })
                        self.algorithm_query_dict[rsp_time] = format_query_data
                        df_algorithm = pd.DataFrame(format_query_data) if format_query_data else ""
                        query_index = rsp_time + "|" + str(len(format_query_data))
                        self.query_algorithm_df[query_index] = df_algorithm
                    if action == "new":
                        instanceid = response["result"]["instructionid"]
                        fundtoken = request["params"]["fund_token"]
                        fund = self.state.fundtoken_dict.get(fundtoken, "")
                        new_algorithm = {
                            "rsp_time": rsp_time,
                            "fund": fund,
                            "inst_id": instanceid,
                            "inst_type": dict_inst_type[request["params"]["instructiontype"]],
                            "security": request["params"]["security"],
                            "side": request["params"]["side"],
                            "qty": request["params"]["qty"],
                            "price": request["params"]["price"],
                            "ptype": request["params"]["pricetype"],
                            "pimit": request["params"]["pricelimit"],
                            "创建后": dict_init_desc[request["params"]["initflag"]],
                            "到期后": dict_expire_desc[request["params"]["expirerevokeflag"]],
                            "取价失败后": dict_special_desc[request["params"]["specialdeal"]],
                        }
                        self.algorithm_list.append(new_algorithm)
                        dict_eop_desc = ["忽略","暂停","废单"]
                        dict_expre2_desc = ["不继续委托", "继续委托"]
                        algorithm_params = request["params"]["instructionparam"]["algorithm"]
                        new_algorithm_detail = {
                            "algorithm": request["params"]["instructionparam"]["algorithmtype"],
                            "交易失败": dict_eop_desc[request["params"]["instructionparam"]["tradeerrop"]],
                            "到期后": dict_expre2_desc[request["params"]["instructionparam"]["tradeexpireoperation"]],
                        }
                        new_algorithm_detail.update({k: v for k, v in algorithm_params.items() if v is not None})
                        if "starttime" in new_algorithm_detail:
                            new_algorithm_detail["starttime"] = datetime.fromtimestamp(new_algorithm_detail["starttime"]).strftime("%Y-%m-%d %H:%M:%S")
                        if "endtime" in new_algorithm_detail:
                            new_algorithm_detail["endtime"] = datetime.fromtimestamp(new_algorithm_detail["endtime"]).strftime("%Y-%m-%d %H:%M:%S")
                        if "needreprice" in new_algorithm_detail and new_algorithm_detail["needreprice"] != "1":
                            new_algorithm_detail.pop("repricetype", None)
                            new_algorithm_detail.pop("reprice", None)
                        if "pricelimittype" not in new_algorithm_detail:
                            new_algorithm_detail.pop("pricefloatuplimit", None)
                            new_algorithm_detail.pop("pricefloatdownlimit", None)
                            new_algorithm_detail.pop("priceuplimit", None)
                            new_algorithm_detail.pop("pricedownlimit", None)
                        new_algorithm_detail.pop("timelimit", None)
                        self.algorithm_detail_dict[instanceid] = new_algorithm_detail

    def handle_algorithm(self):
        df_algorithm = pd.DataFrame(self.algorithm_list)
        return df_algorithm

    def get_algorithm_code(self) -> List[str]:
        """
        Jupyter友好：获取所有涉及证券代码
        """
        security_list = [algorithm["security"] for algorithm in self.algorithm_list]
        return list(set(security_list))

    def get_algorithm_detail(self, instanceid: str) -> Optional[pd.DataFrame]:
        """
        Jupyter友好：获取指定算法单详情
        """
        if instanceid in self.algorithm_detail_dict:
            algorithm_detail = self.algorithm_detail_dict[instanceid]
            df_algorithm_detail = pd.DataFrame([algorithm_detail])
            df_algorithm_detail.rename(columns = {
                "revokeinterval":"补单间隔","rechaseinterval":"补单间隔","minordernumber":"最小子单","maxordernumber":"最大子单",
                "slicetime":"委托间隔","timerand":"随机委托", "randprice":"随机价浮",
                "pricelimittype":"限价类型","pricefloatuplimit":"限价上限","pricefloatdownlimit":"限价下限",
                "needreprice":"补单","entrustlimit":"委托次数限制","startfloat":"浮动启动笔数",
            }, inplace=True)
            return df_algorithm_detail
        return None

    def get_algorithm_push_detail(self, instanceid: str, push_type: str) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
        """
        Jupyter友好：获取算法单推送详情
        """
        import pandas as pd
        dict_pushtype_keep_columns = {
            "instruction":["req_time", "avgpx", "qty", "qtyleft", "qtycancel", "qtytrade", "statusmsg", "msg"],
            "order":["req_time", "orderid", "operationmsg", "avgpx", "price", "qty", "qtyleft", "qtycancel", "qtytrade", "statusmsg", "msg"],
        }
        if instanceid not in self.algorithm_push:
            return None, None
        push_key = next((k for k in self.algorithm_push[instanceid] if push_type in k), None)
        if not push_key:
            return None, None
        push_data = self.algorithm_push[instanceid][push_key]
        df_algorithm_push = pd.DataFrame(push_data, columns = dict_pushtype_keep_columns[push_type])
        return push_key, df_algorithm_push

    # Jupyter友好型方法
    def show_queryalgorithm(self, querytime: str) -> None:
        """
        Jupyter友好：展示算法单查询结果
        """
        df = self.query_algorithm_df.get(querytime, pd.DataFrame())
        print(f"算法单查询结果（{querytime}）：")
        display(df)

    # 仅为原先只有展示型方法的部分新增web友好型接口
    def get_algorithm_query_data(self) -> List[Dict[str, Any]]:
        """
        获取算法单查询结构化数据，适合web接口返回
        """
        result = []
        for df in self.query_algorithm_df.values():
            if isinstance(df, pd.DataFrame):
                result.extend(df.to_dict(orient="records"))
        return result 
