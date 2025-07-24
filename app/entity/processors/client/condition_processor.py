"""
条件交易处理器模块
负责条件单的解析、处理与数据输出
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from .models import ProcessingState, RequestPairsDict, ProcessingConfig
import json

class ConditionProcessor:
    """条件交易处理器类"""
    def __init__(self, state: ProcessingState, req_pairs: RequestPairsDict, base_processor: BaseProcessor):
        self.state = state
        self.req_pairs = req_pairs
        self.base_processor = base_processor
        self.gradecondition_create: List[Dict[str, Any]] = []
        self.gradecondition_info: Dict[str, Any] = {}
        self.gradecondition_push: Dict[str, Any] = {}
        self.gradecondition_query_dict: Dict[str, Any] = {}
        self.query_gradecondition_df: Dict[str, Any] = {}
        self.config = ProcessingConfig()

    def parse_condition_query(self) -> None:
        """
        解析条件单相关数据，包括推送
        """
        self.gradecondition_create = []
        self.gradecondition_info = {}
        self.gradecondition_push = {}
        self.gradecondition_query_dict = {}
        self.query_gradecondition_df = {}
        # 1. 新建母单
        req_list = self.base_processor.get_request_list("json", "rpc.gradecondition", "create_gradecondition")
        for key in req_list:
            item = self.req_pairs[key]
            request = item["request"]
            response = item["response"]
            rsp_time = item["rsp_time"]
            requestdata = request["params"]
            requestdata["rsp_time"] = rsp_time
            order_no = response["result"]["order_no"]
            if order_no not in self.gradecondition_info.keys():
                self.gradecondition_info[order_no] = {"req_id": key, "instruction_params": [], "operations": []}
            requestdata["order_no"] = order_no
            # 如果母单中有 fund_token, 那么转化
            if "fund_token" in request["params"].keys():
                requestdata["fund"] = self.state.fundtoken_dict.get(request["params"]["fund_token"], "")
            self.gradecondition_create.append(requestdata)
            # 如果子单中有fund_token，那么转化
            if "instruction_param" in request["params"].keys():
                instruction_param = request["params"]["instruction_param"]
                for instruction in instruction_param:
                    if "fund_token" in instruction:
                        instruction["fund"] = self.state.fundtoken_dict.get(instruction["fund_token"], "")
                self.gradecondition_info[order_no]["instruction_params"] = instruction_param
        # 2. 母单操作
        operation_cmd = ["delete_gradecondition", "pause_gradecondition", "modify_gradecondition", "activate_gradecondition", "cancel_gradecondition"]
        for action in operation_cmd:
            operation_reqs = self.base_processor.get_request_list("json", "rpc.gradecondition", action)
            for request_key in operation_reqs:
                operation_req = self.req_pairs[request_key]
                request = operation_req["request"]["params"]
                response = {}
                if "result" in operation_req["response"]:
                    response = operation_req["response"]["result"]
                else:
                    response = operation_req["response"]["error"]
                    response["msg"] = response["message"]
                rsp_time = operation_req["rsp_time"]
                order_no = request["order_no"]
                if order_no not in self.gradecondition_info:
                    self.gradecondition_info[order_no] = {"req_id": "", "instruction_params": [], "operations": []}
                request["id"] = operation_req["request"]["id"]
                merged_dict = {**{f"request_{k}" if (k in response and v != response[k]) else k: v for k, v in request.items()},
                               **{f"response_{k}" if (k in request and v != request[k]) else k: v for k, v in response.items()}}
                merged_dict["rsp_time"] = rsp_time
                self.gradecondition_info[order_no]["operations"].append(merged_dict)
        # 3. 推送数据解析
        # 假设 self.state.gradecondition_push_instruction/condition/order 为推送原始数据列表
        if hasattr(self.state, "gradecondition_push_instruction"):
            for rsp_time, rsp_data in self.state.gradecondition_push_instruction:
                pushdata = json.loads(rsp_data)["params"]
                pushdata["rsp_time"] = rsp_time
                order_no = pushdata["order_no"]
                if order_no not in self.gradecondition_push:
                    self.gradecondition_push[order_no] = {"grade_instruction":[],"grade_condition":{},"grade_order":{}}
                self.gradecondition_push[order_no]["grade_instruction"].append(pushdata)
        if hasattr(self.state, "gradecondition_push_condition"):
            for rsp_time, rsp_data in self.state.gradecondition_push_condition:
                pushdata = json.loads(rsp_data)["params"]
                pushdata["rsp_time"] = rsp_time
                order_no = pushdata["order_no"]
                symbol = pushdata["symbol"]
                if order_no not in self.gradecondition_push:
                    self.gradecondition_push[order_no] = {"grade_instruction":[],"grade_condition":{},"grade_order":{}}
                if symbol not in self.gradecondition_push[order_no]["grade_condition"]:
                    self.gradecondition_push[order_no]["grade_condition"][symbol] = []
                self.gradecondition_push[order_no]["grade_condition"][symbol].append(pushdata)
        if hasattr(self.state, "gradecondition_push_order"):
            for rsp_time, rsp_data in self.state.gradecondition_push_order:
                pushdata = json.loads(rsp_data)["params"]
                order_no = pushdata["order_no"]
                symbol = pushdata["data"]["SecurityID"]
                orderdata = pushdata["data"]
                orderdata["rsp_time"] = rsp_time
                if order_no not in self.gradecondition_push:
                    self.gradecondition_push[order_no] = {"grade_instruction":[],"grade_condition":{},"grade_order":{}}
                if symbol not in self.gradecondition_push[order_no]["grade_order"]:
                    self.gradecondition_push[order_no]["grade_order"][symbol] = []
                self.gradecondition_push[order_no]["grade_order"][symbol].append(orderdata)
        # 4. 查询母单
        self.gradecondition_query_dict = self.state._handle_query_result("json", "rpc.gradecondition", "query_gradecondition", "data")
        columns_gradecondition_querydata = ["rsp_time", "fund", "order_from", "order_no", "create_time", "update_time", "status_msg", "price_type", "side", "note"]
        for rsp_time, query_data in self.gradecondition_query_dict.items():
            df_query_gradecondition = ""
            if len(query_data) > 0:
                df_query_gradecondition = pd.DataFrame(query_data, columns=columns_gradecondition_querydata)
            query_index = rsp_time + "|gradecond|" + str(len(query_data))
            self.query_gradecondition_df[query_index] = df_query_gradecondition

    # Jupyter友好型方法
    def show_condition_summary(self) -> None:
        # print("新增条件单情况：暂缺")
        df_gradecondition_create = pd.DataFrame(self.gradecondition_create, columns=self.config.columns["gradecondition_create"])
        df_gradecondition_create.rename(columns = {"algorithm_type":"algorithm", "start_monitor_time":"开始监控", "end_monitor_time":"结束监控"}, inplace=True)
        df_gradecondition_create = df_gradecondition_create.sort_values(by='rsp_time', ascending=True).dropna(axis=1, how="all")
        print("\n当日新增组合条件单情况")
        display(df_gradecondition_create)
        print("\n当日母单操作情况")
        gradecondition_operations = []
        for order_no, order_operations in self.gradecondition_info.items():
            operations = order_operations["operations"]
            for item in operations:
                gradecondition_operations.append(item)
        df_gradecondition_operations = pd.DataFrame(gradecondition_operations, columns=self.config.columns["gradecondition_operate"])
        df_gradecondition_operations = df_gradecondition_operations.sort_values(by='rsp_time', ascending=True).dropna(axis=1, how="all")
        if len(gradecondition_operations) > 0:
            df_gradecondition_operations["action"] = df_gradecondition_operations["action"].apply(lambda x: x.split('_')[0])
        display(df_gradecondition_operations)
        print("母单推送数:%d, 子单推送数:%d, 子单委托推送数:%d" % (
            len(self.state.gradecondition_push_instruction), 
            len(self.state.gradecondition_push_condition),
            len(self.state.gradecondition_push_order)))

    def show_condition_instance_detail(self, order_no: str, fund: str, security: str) -> None:
        if order_no not in self.gradecondition_info:
            print(f"母单[{order_no}]不在新建母单列表中")
        else:
            print("母单创建详情", order_no)
            the_create = next((item for item in self.gradecondition_create if item["order_no"] == order_no), None)
            list_the_create = []
            condition_text = ""
            def get_key_note(key):
                note = ""
                dict_key_2_note = {
                    "order_from":"订单来源",
                    "start_monitor_time":"开始监控时间",
                    "end_monitor_time":"结束监控时间",
                    "trade_interval_time":"交易时间间隔",
                    "basket_name":"篮子名称",
                    "distribute_type":"分配方式",
                    "algorithm_type":"订单算法",
                    "max_trigger_stock":"最大触发数",
                    "rz_priority_flag":"融资优先开关",
                    "splite_order":"拆单规则",
                    "pause_type":"暂停类型",
                }
                if key in dict_key_2_note:
                    return dict_key_2_note[key]
                return note
            if the_create:
                for key, value in the_create.items():
                    value_format = value
                    if key == "note":
                        condition_text = value
                    if type(value) in (dict, list):
                        value_format = f"valuetype is {str(type(value))}, len={len(value)}"
                    list_the_create.append({"请求字段": key, "字段解释": get_key_note(key), "值": value_format})
                print("condition_text", condition_text)
                with pd.option_context("display.max_colwidth", 100, "display.width", 200):
                    display(pd.DataFrame(list_the_create))
            # 母单操作
            print("\n当日母单操作")
            operations = self.gradecondition_info[order_no]["operations"]
            df_gradecondition_operations = pd.DataFrame(operations, columns=self.config.columns["gradecondition_operate"])
            df_gradecondition_operations = df_gradecondition_operations.sort_values(by='rsp_time', ascending=True).dropna(axis=1, how="all")
            if len(operations) > 0:
                df_gradecondition_operations["action"] = df_gradecondition_operations["action"].apply(lambda x: x.split('_')[0])
            display(df_gradecondition_operations)
            # 母单改单前后对比
            modify_information = []
            if the_create:
                modify_information.append(the_create)
            for operation in operations:
                action = operation.get("action", "")
                req_id = operation.get("id", "")
                if action == "modify_gradecondition" and req_id in self.req_pairs:
                    the_modify = self.req_pairs[req_id]["request"]["params"]
                    rsp_time = self.req_pairs[req_id]["rsp_time"]
                    the_modify["rsp_time"] = rsp_time
                    modify_information.append(the_modify)
            if len(modify_information) > 1:
                print("\n母单存在修改")
                df = pd.DataFrame(modify_information, columns=["rsp_time", "action", "start_monitor_time", "end_monitor_time", "note"])
                with pd.option_context("display.max_colwidth", 100, "display.width", 200):
                    display(df)
            # 母单关联股票信息
            detail_params = self.gradecondition_info[order_no]["instruction_params"]
            if detail_params:
                df_gradecondition_detail = pd.DataFrame(detail_params, columns=self.config.columns["gradecondition_create_detail"])
                gradecondition_stocks = list(set(df_gradecondition_detail["symbol"].tolist()))
                print("\n母单关联的股票", len(gradecondition_stocks), gradecondition_stocks)
                if "condition" in df_gradecondition_detail:
                    condition_list = set(df_gradecondition_detail["condition"].to_list())
                    print("\n监控条件列表", condition_list)
                print("\n母单股票委托表")
                display(df_gradecondition_detail)
            # 母单推送详情
            if order_no not in self.gradecondition_push.keys():
                print("\n当前母单无推送信息", order_no)
            else:
                pushdata = self.gradecondition_push[order_no]["grade_instruction"]
                if pushdata:
                    print('\n母单首条推送', json.dumps(pushdata[0]))
                    df_gradecondition_push_instruction = pd.DataFrame(pushdata, columns=self.config.columns["gradecondition_push_instruction"])
                    print('\n母单推送列表')
                    display(df_gradecondition_push_instruction)

    def show_condition_order_detail(self, order_no: str) -> None:
        if order_no not in self.gradecondition_push.keys():
            print(f"母单id: {order_no} 没有子单推送")
        else:
            push_condition = []
            grade_conditions = self.gradecondition_push[order_no].get("grade_condition", {})
            for symbol, condition in grade_conditions.items():
                push_condition.append(condition[-1])
            df_grade_condition = pd.DataFrame(push_condition, columns=self.config.columns["gradecondition_push_condition"])
            if "condition" in df_grade_condition:
                condition_list = set(df_grade_condition["condition"].to_list())
                print("监控条件列表", condition_list)
            print("子单状态表")
            display(df_grade_condition)
            # # 子单推送明细
            # grade_order = self.gradecondition_push[order_no].get("grade_order", {})
            # for symbol, order_list in grade_order.items():
            #     print(f"\n证券代码: {symbol} 子单推送明细")
            #     df_order = pd.DataFrame(order_list)
            #     display(df_order)

    def show_condition_security_order_detail(self, order_no: str, fund: str, security: str) -> None:
        if order_no not in self.gradecondition_push.keys():
            print(f"母单id: {order_no} 没有子单推送")
        else:
            grade_condition = self.gradecondition_push[order_no].get("grade_condition", {})
            if security not in grade_condition:
                print(f"母单下 {order_no} 证券代码 {security} 没有推送记录")
            else:
                print("子单个股下单参数", security)
                condition_params = next((item for item in self.gradecondition_info[order_no]["instruction_params"] if item["symbol"] == security), None)
                print(json.dumps(condition_params))
                print(f"\n子单个股推送结果 {order_no} {security}")
                pushdata = self.gradecondition_push[order_no]["grade_order"].get(security, [])
                df = pd.DataFrame(pushdata, columns=self.config.columns["gradecondition_push_order"])
                if "Text" in df:
                    msg_list = [item["Text"] for item in pushdata]
                    print("错误信息列表", set(msg_list))
                display(df)

    def show_condition_initreqs(self, order_no: str, isfullreqs: bool = False) -> None:
        req_id = ""
        if order_no in self.req_pairs.keys():
            req_id = order_no
        if order_no in self.gradecondition_info.keys():
            req_id = self.gradecondition_info[order_no]["req_id"]
        if req_id != "":
            self.base_processor.show_request_and_response(req_id, isfullreqs)
        else:
            print(f"找不到id[{order_no}]关联的原始请求信息")

    def show_querycondition(self, querytime: str) -> None:
        df_query_condition = self.query_gradecondition_df.get(querytime, pd.DataFrame())
        if isinstance(df_query_condition, pd.DataFrame) and not df_query_condition.empty:
            display(df_query_condition)
        else:
            print("本次条件单查询结果为空")

    # Web友好型接口（仅为展示型方法补充结构化数据输出）
    def get_condition_summary_data(self) -> Dict[str, Any]:
        """
        获取条件单汇总结构化数据，适合web接口返回
        """
        return {
            "create": self.gradecondition_create,
            "info": self.gradecondition_info,
            "push": self.gradecondition_push
        }

    def get_condition_instance_detail_data(self, order_no: str) -> Dict[str, Any]:
        """
        获取指定母单详情结构化数据，包含推送明细，适合web接口返回
        """
        info = self.gradecondition_info.get(order_no, {})
        push = self.gradecondition_push.get(order_no, {})
        return {
            "info": info,
            "push": push
        }

    def get_condition_order_detail_data(self, order_no: str) -> Dict[str, Any]:
        """
        获取母单子单推送结构化数据，包含子单状态和推送明细，适合web接口返回
        """
        if order_no not in self.gradecondition_push:
            return {"status": [], "push_detail": {}}
        push_condition = []
        grade_conditions = self.gradecondition_push[order_no].get("grade_condition", {})
        for symbol, condition in grade_conditions.items():
            push_condition.append(condition[-1])
        grade_order = self.gradecondition_push[order_no].get("grade_order", {})
        return {
            "status": push_condition,
            "push_detail": grade_order
        }

    def get_condition_security_order_detail_data(self, order_no: str, fund: str, security: str) -> Dict[str, Any]:
        """
        获取母单下指定证券的子单推送结构化数据，包含推送明细和错误信息，适合web接口返回
        """
        if order_no not in self.gradecondition_push:
            return {"push_detail": [], "error_msgs": []}
        grade_order = self.gradecondition_push[order_no].get("grade_order", {})
        pushdata = grade_order.get(security, [])
        error_msgs = [item["Text"] for item in pushdata if "Text" in item]
        return {
            "push_detail": pushdata,
            "error_msgs": list(set(error_msgs))
        }

    def get_condition_initreqs_data(self, order_no: str) -> Any:
        """
        获取母单原始请求信息结构化数据，适合web接口返回
        """
        req_id = ""
        if order_no in self.req_pairs:
            req_id = order_no
        if order_no in self.gradecondition_info:
            req_id = self.gradecondition_info[order_no]["req_id"]
        if req_id != "" and req_id in self.req_pairs:
            return self.req_pairs[req_id]
        return None

    def get_querycondition_data(self, querytime: str) -> Any:
        """
        获取条件单查询结构化数据，适合web接口返回
        """
        df_query_condition = self.query_gradecondition_df.get(querytime, None)
        if isinstance(df_query_condition, pd.DataFrame):
            return df_query_condition.to_dict(orient="records")
        return None 
