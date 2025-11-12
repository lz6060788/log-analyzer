"""
篮子交易处理器模块
负责篮子订单的解析、处理与数据输出
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from .models import ProcessingState, RequestPairsDict, ProcessingConfig
from .base_processor import BaseProcessor

class BasketProcessor:
    """篮子交易处理器类"""
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict, base_processor: BaseProcessor):
        self.state = state
        self.req_pairs = req_pairs
        self.base_processor = base_processor
        self.config = ProcessingConfig()
        print(self.config.columns)
        # 数据存储
        # 单户委托
        self.singleorder_list: List[Dict[str, Any]] = []
        # 单户撤单
        self.singleorder_cancellist: List[Dict[str, Any]] = []
        # 多户交易
        self.basketorder_list: List[Dict[str, Any]] = []
        # 多户撤单/撤补
        self.basketorder_op_list: List[Dict[str, Any]] = []
        # 母单详情
        self.basketorder_detail_dict: Dict[str, List[Dict[str, Any]]] = {}
        # 母单信息
        self.basketorder_info: Dict[str, Any] = {}
        # 推送数据
        self.basketorder_push = {}


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

    def parse_basket_query(self) -> None:
        """
        解析篮子订单相关数据，包括推送
        """
        self.singleorder_list = []
        self.singleorder_cancellist = []
        self.basketorder_list = []
        self.basketorder_op_list = []
        self.basketorder_detail_dict = {}
        self.basketorder_info = {}
        self.basketorder_push = {}
        self.basketorder_query_dict = {}
        # 篮子订单查询
        req_list = self._get_request_list("json", "basket", "QryBasketOrder")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value.get("req_time", None)
            rsp_time = value["rsp_time"]
            querydata = response["result"]
            self.basketorder_query_dict[f"{rsp_time}|{len(querydata)}|{key}"] = querydata
        # 单户交易
        req_list = self._get_request_list("pb", "rpc.order.manager", "insert_order_jgb")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            rsp_time = value["rsp_time"]
            handledata = request["params"].copy()
            if "result" in response.keys():
                handledata["code"] = response["result"]["code"]
            else:
                handledata["code"] = response["error"]["code"]
                handledata["message"] = response["error"].get("message", "")
            handledata["rsp_time"] = rsp_time
            handledata["req_id"] = key
            handledata["fund"] = self._get_fund_by_fund_token(request["params"]["fund_token"])
            self.singleorder_list.append(handledata)
        # 单户撤单
        req_list = self._get_request_list("pb", "rpc.order.manager", "cancel_order_jgb")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            rsp_time = value["rsp_time"]
            handledata = request["params"].copy()
            if "result" in response.keys():
                handledata["code"] = response["result"]["code"]
            else:
                handledata["code"] = response["error"]["code"]
                handledata["message"] = response["error"].get("message", "")
            handledata["rsp_time"] = rsp_time
            handledata["fund"] = self._get_fund_by_fund_token(request["params"]["fund_token"])
            self.singleorder_cancellist.append(handledata)
        # 多户交易
        req_list = self._get_request_list("json", "basket", "BasketOrder")
        req_list += self._get_request_list("json", "basket", "InstructionOrder")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            rsp_time = value["rsp_time"]
            instanceid = request["params"]["InstanceID"]
            result = {
                "rsp_time": rsp_time,
                "instanceid": instanceid,
                "source": request["params"].get("ClientOrderType", ""),
                "fund_num": 0,
                "security_num": 0,
                "side": request["params"].get("Side", ""),
                "note": request["params"].get("Note", ""),
            }
            if instanceid not in self.basketorder_info.keys():
                self.basketorder_info[instanceid] = {"req_id": key, "order_list": {}}
            basketorder_detail = request["params"]["OrderBase"]
            security_list = set([item["SecurityID"] for item in basketorder_detail])
            result["security_num"] = len(security_list)
            fund_list = set([self._get_fund_by_fund_token(item["fund_token"]) for item in basketorder_detail])
            result["fund_num"] = len(fund_list)
            self.basketorder_list.append(result)
            for item in basketorder_detail:
                item["fund"] = self._get_fund_by_fund_token(item["fund_token"])
                self.basketorder_detail_dict[instanceid] = basketorder_detail
        # 多户撤单/撤补
        req_list = self._get_request_list("json", "basket", "OrderAction")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            rsp_time = value["rsp_time"]
            handledata = request["params"].copy()
            handledata["rsp_time"] = rsp_time
            handledata["result"] = response["result"]["code"] if "result" in response else None
            self.basketorder_op_list.append(handledata)
        # 推送解析
        if hasattr(self.state, "basketorder_push_raw"):
            for req_time, raw_response in self.state.basketorder_push_raw:
                import json
                response_json = json.loads(raw_response)
                response_dict = response_json["params"]["data"]
                if "MarketID" in response_dict:
                    MarketID = str(response_dict["MarketID"])
                else:
                    MarketID = ""
                if MarketID:
                    if "SecurityID" not in response_dict:
                        continue
                    InstanceID = response_dict["InstanceID"]
                    print(self.state.client_fundtoken_mapping)
                    fund_token = self.state.client_fundtoken_mapping[response_dict["fund_token"]]
                    # fund_token = response_dict.get("fund_token", "")
                    code = response_dict["SecurityID"]
                    fund_key = f'{fund_token}|{code}'
                    response_dict["PushTime"] = req_time
                    if fund_token != "":
                        if hasattr(self.state, "fundtoken_dict") and fund_token in self.state.fundtoken_dict:
                            response_dict["fund"] = self.state.fundtoken_dict[fund_token]
                    if InstanceID not in self.basketorder_push:
                        self.basketorder_push[InstanceID] = {}
                    if fund_key not in self.basketorder_push[InstanceID]:
                        self.basketorder_push[InstanceID][fund_key] = []
                    self.basketorder_push[InstanceID][fund_key].append(response_dict)

    def handle_basketorder(self) -> List[str]:
        """
        返回订单来源类型列表
        """
        source_list = list(set([item["source"] for item in self.basketorder_list]))
        source_list.insert(0, "全部")
        return source_list

    def get_basketorder_code(self):
        """
        获取所有涉及的证券代码列表，与clientprocessor.py一致
        """
        security_list = []
        for key, detail in self.basketorder_detail_dict.items():
            for item in detail:
                security_list.append(item["SecurityID"])
        distinct_security_list = list(set(security_list))
        return distinct_security_list
    def get_basketorder_detail(self, instanceid):
        """
        获取指定母单的子单明细，DataFrame格式，与clientprocessor.py一致
        """
        import pandas as pd
        if instanceid in self.basketorder_detail_dict.keys():
            basketorder_detail = self.basketorder_detail_dict[instanceid]
            df_basketorder_detail = pd.DataFrame(basketorder_detail, columns = [
                "fund_token", "fund", "SecurityID", "MarketID", "Side", "OrderQty", "OrderPrice", "PriceType"
            ])
            return df_basketorder_detail

    def get_basketorder_push_detail(self, instanceid, fund_key):
        """
        获取指定母单和资金的推送明细，DataFrame格式，与clientprocessor.py一致
        """
        push_data = self.basketorder_push[instanceid][fund_key]
        df_basketorder_push = pd.DataFrame(push_data, columns = [
            "PushTime","SecurityID", "MarketID", "Side", "OrderPrice", "OrderQty", "TradeVolume", "OrderID",
            "OrderTypeMsg", "OperationMsg", "OrderTime", "OrderStatusMsg", "Text"
        ])
        df_basketorder_push.rename(columns = {
            "OrderTypeMsg":"OrderType", "OperationMsg":"Op", "OrderStatusMsg":"OrderStatus",
        }, inplace=True)
        return df_basketorder_push 

    def handle_basket_query(self):
        """
        所有篮子订单查询结果，与clientprocessor.py一致
        """
        querytime_list = list(self.basketorder_query_dict.keys())
        return querytime_list

    def get_basket_summary_data(self, source: Optional[str] = None, fund: str = "", stockcode: str = "") -> List[Dict[str, Any]]:
        """
        获取订单汇总数据，适合web接口返回
        Args:
            source: 订单来源类型
            fund: 资金账号筛选
            stockcode: 证券代码筛选
        Returns:
            母单数据列表
        """
        result = {}

        df_singleorder = pd.DataFrame(self.singleorder_list, columns=self.config.columns["singleorder"])
        df_singleorder_success = df_singleorder[df_singleorder["code"] == 0]
        result["singleorder_success"] = df_singleorder_success
        df_singleorder_failed = df_singleorder[df_singleorder["code"] != 0]
        message_list = [item.get("message", "") for item in self.singleorder_list if item["code"] != 0]
        result["singleorder_failed"] = df_singleorder_failed
        result["singleorder_failed_message"] = message_list
        df_singleorder_cancel = pd.DataFrame(self.singleorder_cancellist, columns=self.config.columns["singleorder_cancel"])
        result["singleorder_cancel"] = df_singleorder_cancel

        # 根据source、fund、stockcode筛选母单
        filtered_instanceid_bysource = [item["instanceid"] for item in self.basketorder_list if (source == "全部" or (item["source"] == source))]
        filtered_instanceid = []
        for instanceid, basketitem in self.basketorder_detail_dict.items():
            if instanceid in filtered_instanceid_bysource:
                filterfund = False
                filtercode = False
                for item in basketitem:
                    if fund == "" or (fund != "" and fund in item["fund"]):
                        filterfund = True
                    if stockcode == "" or (stockcode != "" and stockcode == item["SecurityID"]):
                        filtercode = True
                if filterfund and filtercode:
                    filtered_instanceid.append(instanceid)
        filtered_basketorder = [item for item in self.basketorder_list if item["instanceid"] in filtered_instanceid]

        security_list = []
        for instanceid in filtered_instanceid:
            for item in self.basketorder_detail_dict[instanceid]:
                security_list.append(item["SecurityID"])
        distinct_security_list = list(set(security_list))
        result["distinct_security_list"] = distinct_security_list
        df_basketorder = pd.DataFrame(filtered_basketorder)
        result["basketorder"] = df_basketorder
        filted_op_list = [item for item in self.basketorder_op_list if item.get("InstanceID") in filtered_instanceid]
        df_basketorder_op = pd.DataFrame(filted_op_list)
        result["basketorder_op"] = df_basketorder_op
        return result

    def get_basket_instance_detail(self, instanceid: str) -> Dict[str, Any]:
        """
        web友好：获取指定母单的实例详情
        """
        result = {}
        if instanceid == "":
            raise ValueError("instanceid不能为空")
        else:
            req_id = self.basketorder_info[instanceid]["req_id"]
            value = self.req_pairs[req_id]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            the_create = request["params"]
            list_the_create = []
            for key, value in the_create.items():
                value_format = value
                if type(value) in (list, dict):
                    value_format = "valuetype is %s, len=%d" % (str(type(value)), len(value))
                list_the_create.append({"请求字段":key, "值":value_format})
            result["the_create"] = pd.DataFrame(list_the_create)
            result["basketorder_detail"] = pd.DataFrame(self.basketorder_detail_dict[instanceid],
                columns=["fund", "SecurityID", "Side", "OrderQty", "OrderPrice", "MarketID", "PriceType"])
            result["response"] = response
            result["req_time"] = req_time
            result["rsp_time"] = rsp_time
            return result

    def get_basket_order_detail(self, instanceid: str, fund: str = "", stockcode: str = "") -> Dict[str, Any]:
        result = []
        if hasattr(self, "basketorder_push") and instanceid in self.basketorder_push:
            for fund_key, pushdata in self.basketorder_push[instanceid].items():
                print(fund_key)
                fund_token = fund_key.split("|")[0]
                fundinfo = self._get_fund_by_fund_token(fund_token)
                if fund == "" or (fund != "" and fund in fundinfo):
                    df_basketorder_push = pd.DataFrame(pushdata, columns = [
                        "PushTime","SecurityID", "MarketID", "Side", "OrderPrice", "OrderQty", "TradeVolume", "OrderID",
                        "OrderTypeMsg", "OperationMsg", "OrderTime", "OrderStatusMsg", "Text"
                    ])
                    df_basketorder_push.rename(columns = {
                        "TradeVolume":"Volume", "OrderPrice":"Price", "MarketID":"Market",
                        "OrderTypeMsg":"OrderType", "OperationMsg":"OP", "OrderStatusMsg":"OrderStatus"
                    }, inplace=True)
                    if stockcode != "":
                        df_basketorder_push = df_basketorder_push[df_basketorder_push["SecurityID"] == stockcode]
                    records = df_basketorder_push.to_dict(orient="records")
                    # 为每条记录添加fundinfo字段
                    for rec in records:
                        rec["fundinfo"] = fundinfo
                        rec["fund_token"] = fund_token
                    result.append(records)
            return result
        else:
            return []

    def get_basket_query_data(self, querytime = None):
        """
        web友好：获取某次篮子订单查询的结果
        """
        if querytime is None:
            result = {}
            for querytime, querydata in self.basketorder_query_dict.items():
                df_querydata = pd.DataFrame(querydata, columns=[
                    "CreateDate", "CreateTime", "InstanceID", "ClientOrderType",  "OrderQty", "DealVolume", "CancelOrderQty", "OperationMsg","Text"
                ])
                df_querydata_sorted = df_querydata.sort_values(by="CreateTime", ascending=True)
                result[querytime] = df_querydata_sorted.to_dict(orient="records")
            return result
        else:
            querydata = self.basketorder_query_dict[querytime]
            result = []
            if len(querydata) > 0:
                df_querydata = pd.DataFrame(querydata, columns=[
                    "CreateDate", "CreateTime", "InstanceID", "ClientOrderType",  "OrderQty", "DealVolume", "CancelOrderQty", "OperationMsg","Text"
                ])
                df_querydata_sorted = df_querydata.sort_values(by="CreateTime", ascending=True)
                result = df_querydata_sorted
            return result

    def get_basket_initreqs(self, instance):
        """
        web友好：获取母单的原始请求明细
        """
        req_id = ""
        if instance in self.req_pairs.keys():
            req_id = instance
        if instance in self.basketorder_info.keys():
            req_id = self.basketorder_info[instance]["req_id"]
        if req_id != "":
            return self.base_processor.get_request_and_response(req_id)
        else:
            return None

