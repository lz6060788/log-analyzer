import json
import traceback
import re
import time
from datetime import datetime
import pandas as pd

class ClientProcessor:
    def __init__(self, file_list):
        pd.set_option('display.max_rows', 50)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        
        self.split_map = {
            "request":"&send=",
            "response":"&recv=",
        }
        self.req_time_map = {
            "request":"req_time",
            "response":"rsp_time"
        }
        self.skip_word = ['|timeout|']
        self.req_pairs = {}
        self.request_statics = {"pb":{},"json":{},"json_funid":{}}
        self.illegal_reqs = []
        self.timeout_reqs = []
        self.skipped_reqs = []
        self.new_transmit_reqs = []
        self.response_without_reqid = []
        self.lines_without_reqid = []
        self.skipped_reqpairs = {}
        self.userid = ""
        self.username = ""
        self.log_begin_time = ""
        self.log_end_time = ""
        self.columns = {
            "singleorder":["rsp_time", "fund", "req_id", "order_source", "symbol", "price", "quantity", "side", "code"],
            "singleorder_failed":["rsp_time", "fund", "req_id", "symbol", "code", "message"],
            "singleorder_cancel":["rsp_time", "fund", "fund_token", "order_no", "exchange", "side", "code", "message"],
            "basketorder_cancel":["rsp_time", "action", "InstanceID", "Supplement", "result"],
            "gradecondition_create":["rsp_time", "fund", "basket_name", "order_from", "order_no", "side","max_trigger_stock", "start_monitor_time", "end_monitor_time", "distribute_type"],
            "gradecondition_create_detail":["fund", "condition", "algorithm_type", "exchange_type", "symbol", "balance", "qty", "side", "price", "price_type"],
            "gradecondition_operate":["rsp_time", "action", "id", "order_no", "status_msg", "msg"],
            "gradecondition_push_instruction":["rsp_time", "grade_status", "status_msg","current_order_qty", "current_order_trigger_qty", "condition_size", "trade_order_qty", "traded_balance"],
            "gradecondition_push_condition":["rsp_time", "symbol", "side", "condition", "status_msg", "trigger_time", "qty", "qty_order", "qty_trade", "algorithm_type"],
            "gradecondition_push_order":["rsp_time", "OrderEntryTime", "SecurityID", "MarketID", "Side", "OrderID", "OrderPrice", "OrderQty", "OrderTypeMsg", "OrderStatusMsg", "Currency", "AvgPx"],
        }
        # 查询账户列表
        self.query_accounts = {}
        self.query_accounts_df = {}
        self.fundtoken_dict = {}  # 资金账户的fund_token 对应映射名称
        self.fund_dict = {}       # 资金账户:账户类型 对应映射名称
        self.client_fundtoken_mapping = {}
        self.client_permissioncode_mapping = {}
        # 查询资金
        self.query_account_asset_dict = {}
        self.query_rzrq_account_asset_dict = {}
        self.query_ggt_account_asset_dict = {}
        self.query_asset_failed_list = []
        pd.set_option('display.float_format', '{:.2f}'.format)
        # 查询持仓
        self.query_account_stock_dict = {}
        self.query_rzrq_account_stock_dict = {}
        self.query_ggt_account_stock_dict = {}
        self.query_stock_failed_list = []
        # 查询委托
        self.query_order_dict = {}
        self.query_rzrq_order_dict = {}
        self.query_ggt_order_dict = {}
        self.query_order_df = {}
        # 查询成交
        self.query_trade_dict = {}
        self.query_rzrq_trade_dict = {}
        self.query_ggt_trade_dict = {}
        self.query_trade_df = {}
        # 新股申购
        self.xgsg_query_list = []
        # 查询可融资标的券列表
        self.query_finable_security_dict = {}
        self.current_finable_security = ""
        self.finable_security_dict = {}
        # 篮子交易
        self.singleorder_list = []
        self.singleorder_cancellist = []
        self.basketorder_list = []
        self.basketorder_op_list = []
        self.basketorder_detail_dict = {}
        self.basketorder_push_raw = []
        self.basketorder_push = {}
        self.basketorder_push_cnts = 0
        # 算法交易
        self.possible_algorithm_pushkey = [
            "twap_instruction", "twap_order", "twap_trade",
            "twapplus_instruction", "twapplus_order", "twapplus_trade",
            "iceberg_instruction", "iceberg_order", "iceberg_trade",
        ]
        self.algorithm_push_raw = []
        self.algorithm_push = {}
        self.algorithm_list = []
        self.algorithm_detail_dcit = {}
        self.algorithm_query_dict = {}
        self.query_algorithm_df = {}
        # 条件交易
        self.gradecondition_query_dict = {}
        self.query_gradecondition_df = {}
        self.gradecondition_create = []
        self.grade_condition_info = {}
        self.gradecondition_push = {}
        self.gradecondition_push_instruction = []
        self.gradecondition_push_condition = []
        self.gradecondition_push_order = []
        
        self.file_list = file_list
        
        
    def _create_fundtoken_dict(self, row):
        value_str = f"{row['account_code']}:{row['broker_name']}:{row['trade_type']}"
        return (row["fund_token"], value_str)
        
        
    def _create_fund_dict(self, row):
        value_str = f"{row['account_code']}:{row['broker_name']}:{row['trade_type']}"
        value_key = f"{row['account_code']}:{row['trade_type']}"
        return (value_key, value_str)


    def _find_key_in_dict(self, d, target_key):
        found_values = []
        def recursive_search(subdict):
            if isinstance(subdict, dict):
                for key, value in subdict.items():
                    if key == target_key:
                        found_values.append(value)
                    if isinstance(value, (dict, list)):
                        recursive_search(value)
            elif isinstance(subdict, list):
                for item in subdict:
                    recursive_search(item)
        recursive_search(d)
        return found_values


    def _is_altorithm_push(self, line, d):
        for key in d:
            if key in line:
                return True
        return False


    def parse_line(self, line):
        if "new_transmit_" in line:
            self.new_transmit_reqs.append(line)
            return ""
        # elif any(skip in line for skip in self.skip_word):
        elif "|timeout|" in line:
            self.timeout_reqs.append(line)
            return ""
        elif not "|" in line:
            self.skipped_reqs.append(line)
            return ""
        try:
            req_time = line.split('|')[1]
            req_type = line.split('|')[2]
            log_level = line.split('|')[3]
            req_id = line.split('|')[4]
        except Exception as e:
            print(f"parse line error: {e}")
            return ""
        
        if self.log_begin_time == "":
            self.log_begin_time = req_time
        self.log_end_time = req_time
        
        if req_id != "":
            if req_id not in self.req_pairs.keys():
                self.req_pairs[req_id] = {"request":"", "response":"", "req_time":"", "rsp_time":"", "protocol":""}
            try:
                # 兼容一下返回 xxx&recv= 的情况
                split_line = line.split(self.split_map[req_type])
                req_split = split_line[1] if (len(split_line) > 1 and len(split_line[1]) > 2) else '{}'
                req_split = req_split.replace("******", "}]}}}},")
                req_split = req_split.replace("\r\n", "")
                req_json = json.loads(req_split)

                self.req_pairs[req_id][req_type] = req_json
                self.req_pairs[req_id][self.req_time_map[req_type]] = req_time
                
                # 根据请求类型，设置请求 protocol
                if req_type == "request":
                    if "servicename" in line:
                        self.req_pairs[req_id]["protocol"] = "pb"
                    elif "FunID" in line:
                        self.req_pairs[req_id]["protocol"] = "json_funid"
                    elif "action" in line:
                        self.req_pairs[req_id]["protocol"] = "json"
                # 如果用户姓名为空，那么每个请求找一下
                if self.username == "":
                    if "useraccount" in req_split:
                        username_list =  self._find_key_in_dict(req_json, "useraccount")
                        self.username = username_list
            
            except Exception as e:
                self.illegal_reqs.append({
                    "line":line,
                    "e":e,
                    "traceback_exc":traceback.format_exc(),
                })
                return ""
        # 查询账户，没有req_id，特殊处理
        elif "query accout result" in line:
            try:
                req_split = line.split(self.split_map['request'])[1]
                # 适配一下logbody有多条的情况
                logbody = json.loads(req_split)["params"]["logbody"]
                user_account_str = ""
                for item in logbody:
                    if item["event"] == "query accout result!":
                        user_account_str = item["msg"].replace("InitAccountList:: result", "")[1:-1]
                    self.userid = item["userid"]
                self.query_accounts[req_time] = user_account_str
            except:
                pass
        # 集中交易、篮子交易推送，没有req_id，特殊处理
        # 这里解析用到了fundtoken_dict数据，得先保存，后续解析
        elif "basket_order_push" in line:
            request_str = line.split(self.split_map["response"])[1]
            self.basketorder_push_raw.append([req_time, request_str])
            self.basketorder_push_cnts += 1
        # 算法交易推送
        elif self._is_altorithm_push(line, self.possible_algorithm_pushkey):
            request_str = line.split(self.split_map["response"])[1]
            self.algorithm_push_raw.append([req_time, request_str])
        # 组合条件推送
        elif "grade_instruction" in line:
            request_str = line.split(self.split_map["response"])[1]
            self.gradecondition_push_instruction.append([req_time, request_str])
        elif "grade_condition" in line:
            request_str = line.split(self.split_map["response"])[1]
            self.gradecondition_push_condition.append([req_time, request_str])
        elif "grade_order" in line:
            request_str = line.split(self.split_map["response"])[1]
            self.gradecondition_push_order.append([req_time, request_str])
        else:
            if req_type == "response":
                request_str = line.split(self.split_map["response"])[1]
                self.response_without_reqid.append([req_time, request_str])
            else:
                self.lines_without_reqid.append(line)
                # break

    def parse(self):
        self.req_pairs = {}
        self.query_accounts = {}
        self.basketorder_push_cnts = 0
        for file_content in self.file_list:
            for line in file_content.split("\n"):
                self.parse_line(line)
        # 去除为空的请求
        self.removed_reqs = {key:value for key, value in self.req_pairs.items() 
                             if (len(json.dumps(value["request"])) <= 2 or len(json.dumps(value["response"])) <= 2)}
        self.req_pairs = {key:value for key, value in self.req_pairs.items() 
                          if (len(json.dumps(value["request"])) > 2 and len(json.dumps(value["response"])) > 2)}


    def format_size(self, size):
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024.0:
                return f"{size:.1f}{unit}" if unit != 'B' else f"{int(size)}{unit}"
            size /= 1024.0
        return f"{size:.1f}P"
    
    
    def show_request_statics(self):
        t1 = time.perf_counter()
        self.request_statics = {"pb":{},"json":{},"json_funid":{}}
        request_statics = self.request_statics
        counts = 0
        counts_pb = 0
        counts_json = 0
        counts_funid = 0
        for key, item in self.req_pairs.items():
            counts += 1
            request = item["request"]
            req_time = item["req_time"]
            req_type = item["protocol"]
            servicename = ""
            action = ""
            if req_type == "pb":
                counts_pb += 1
                try:
                    if "servicename" in json.dumps(request):
                        servicename = request["servicename"]
                        if servicename not in [
                            "asset-product-api", "asset-institution-api", "asset-index-api",
                            "rpc.authenticate", "rpc.quota", "rpc.order.manager", "rpc.marketdata",
                            "rpc.trader.stock", "rpc.risk", "rpc.condition", "rpc.grid", "rpc.subcenter",
                        ]:
                            action = request["params"]["action"]
                        else:
                            action = request["method"]
                except Exception as e:
                    print(key, request)
                    break
            elif req_type == "json":
                counts_json += 1
                try:
                    if "servicename" in json.dumps(request):
                        servicename = request["servicename"]
                    else:
                        servicename = request["method"]
                    action = request["params"]["action"]
                except Exception as e:
                    print(key, request)
                    break
            elif req_type == "json_funid":
                counts_funid += 1
                servicename = request["method"]
                action = str(request["params"]["FunID"])
            if not servicename in request_statics[req_type].keys():
                request_statics[req_type][servicename] = {}
            if action not in request_statics[req_type][servicename].keys():
                request_statics[req_type][servicename][action] = []
            request_statics[req_type][servicename][action].append({"key":key, "lens":len(json.dumps(item)), "req_time":req_time})
        
        cnt = 0
        sum_requests = []
        for k1, v1 in request_statics.items():
            for k2, v2 in request_statics[k1].items():
                for k3, v3 in request_statics[k1][k2].items():
                    total_lens = sum(d["lens"] for d in v3)
                    sum_requests.append({"protocol":k1, "servicename":k2, "action":k3, "counts":len(v3), "avg_lens":self.format_size(total_lens/len(v3)), "total_lens":self.format_size(total_lens)})
                    cnt += len(v3)
        print("总请求数：%d. pb请求数：%d, json请求数：%d, funid请求数：%d. 统计请求数：%d, 统计结果:【%s】" % (counts, counts_pb, counts_json, counts_funid, cnt, cnt==(counts_pb+counts_json+counts_funid)))
        print("统计耗时：", time.perf_counter() - t1)
        return sum_requests


    def get_fund_by_fund_token(self, fund_token):
        if fund_token in self.fundtoken_dict.keys():
            return self.fundtoken_dict[fund_token]
        else:
            return fund_token


    def get_request_list(self, protocol, servicename, cmd):
        request_statics = self.request_statics
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


    def _handle_once_account_query(self, query_data):
        result = []
        for item in query_data:
            fund_token = item["portfolios"][0]["fund_token"]
            if fund_token in self.client_fundtoken_mapping.keys():
                fund_token = self.client_fundtoken_mapping[fund_token]
            result.append({
                "user_id":item["user_id"],
                "fund_token":fund_token,
                "account_code":item["account_code"],
                "account_name":item["account_name"],
                "alias":item["alias"],
                "broker_name":item["broker_name"],
                "broker_id":item["qsid"],
                "trade_type":item["trade_type"],
            })
        df_user_account = pd.DataFrame(result, columns = [
            "user_id", "fund_token", "account_code", "account_name", "alias", "broker_id", "broker_name", "trade_type"
        ])
        return df_user_account
    
    
    # 固定返回格式 { "query_time":[raq_querydata]}
    def _handle_query_result(self, protocol, servicename, cmd, resultkey):
        req_list = self.get_request_list(protocol, servicename, cmd)
        rsp_query_data = {}
        for key in req_list:
            reqs = self.req_pairs[key]
            request = reqs["request"]
            response = reqs["response"]
            rsp_time = reqs["rsp_time"]
            raw_querydata = []
            querydata = response["result"][resultkey]
            for item in querydata:
                raw_item = {}
                fund_token = item["fund_token"]
                raw_item["rsp_time"] =  rsp_time
                raw_item["fund"] = fund_token
                for key, value in item.items():
                    if type(value) == dict:
                        for k1, v1 in value.items():
                            new_key = key + "|" + k1
                            raw_item[new_key] = v1
                    else:
                        raw_item[key] = value
                raw_querydata.append(raw_item)
            if not rsp_time in rsp_query_data.keys():
                rsp_query_data[rsp_time] = raw_querydata
        return rsp_query_data
        
        
    def show_request_and_response(self, req_id, isfullreqs=True):
        item = self.req_pairs[req_id]
        request = item["request"]
        response = item["response"]
        req_time = item["req_time"]
        rsp_time = item["rsp_time"]
        print("request %s %s" % (req_time, self.format_size(len(json.dumps(request)))))
        if isfullreqs:
            print(json.dumps(request))
        print("-"*100)
        print("response %s %s" % (rsp_time, self.format_size(len(json.dumps(response)))))
        if isfullreqs:
            print(json.dumps(response))
        print("-"*100)
    
    
    def handle_account_query(self, req_time = ""):
        for query_time, user_account_str in self.query_accounts.items():
            user_account_dict = json.loads(user_account_str)["result"]["data"]["account_fn"]["list_account_portfolio"]["edges"]
            df_user_account = self._handle_once_account_query(user_account_dict)
            self.query_accounts_df[query_time] = df_user_account
            self.fundtoken_dict.update({k:v for k, v in df_user_account.apply(self._create_fundtoken_dict, axis=1)})
            self.fund_dict.update({k:v for k, v in df_user_account.apply(self._create_fund_dict, axis=1)})
        # 从update_fund_info中拿客户端缓存的fund_token与后台生成的fund_token之间的对应关系
        for key, value in self.req_pairs.items():
            if "upload_fund_info" in json.dumps(value["request"]):
                request = value["request"]
                response = value["response"]
                if "error" not in response.keys():
                    query_string = request["params"]["query"]
                    match = re.search(r',fund_token:"([^"]+)"', query_string)
                    token_a = ""
                    if match:
                        token_a = match.group(1)
                    token_b = response["result"]["data"]["account_fn"]["upload_fund_info"]["fund_info"][0]["fund_token"]
                    permission_code = response["result"]["data"]["account_fn"]["upload_fund_info"]["fund_info"][0]["permission_code"]
                    fund_name = response["result"]["data"]["account_fn"]["upload_fund_info"]["fund_info"][0]["account_name"]
                    self.client_fundtoken_mapping[token_b] = token_a
                    self.client_permissioncode_mapping[token_b] = 'fund_name:%s,permission_code:%s' % (fund_name, permission_code)
        # 从list_account_portfolio中拿账户信息
        for key, value in self.req_pairs.items():
            checkstr = json.dumps(value["request"])
            # 不带with_permission的list_account_portfolio请求是投后分析发起的，需要过滤
            if "list_account_portfolio" in checkstr and "with_permission" in checkstr:
                request = value["request"]
                response = value["response"]
                rsp_time = value["rsp_time"]
                user_account_dict = response["result"]["data"]["account_fn"]["list_account_portfolio"]["edges"]
                df_user_account = self._handle_once_account_query(user_account_dict)
                self.query_accounts_df[rsp_time] = df_user_account
                self.fundtoken_dict.update({k:v for k, v in df_user_account.apply(self._create_fundtoken_dict, axis=1)})
                self.fund_dict.update({k:v for k, v in df_user_account.apply(self._create_fund_dict, axis=1)})

        if req_time in self.query_accounts_df.keys():
            return self.query_accounts_df[req_time]
        if req_time == "":
            return self.query_accounts_df
        
        
    def handle_basket_order_push(self):
        for req_time, raw_response in self.basketorder_push_raw:
            response_json = json.loads(raw_response)
            response_dict = response_json["params"]["data"]
            if "MarketID" in response_dict.keys():
                MarketID = str(response_dict["MarketID"])
            # 过滤母单推送  有效 MarketID  1，2，3，81，82，91，92
            if MarketID:
                if "SecurityID" not in response_dict.keys():
                    continue
                InstanceID = response_dict["InstanceID"]
                fund_token = self.client_fundtoken_mapping[response_dict["fund_token"]]
                code = response_dict["SecurityID"]
                fund_key = '%s|%s' % (fund_token, code)
                response_dict["PushTime"] = req_time
                if fund_token != "":
                    if fund_token in self.fundtoken_dict.keys():
                        response_dict["fund"] = self.get_fund_by_fund_token(fund_token)
                else:
                    user_token = response_dict["fund_token"]
                    if user_token in self.fundtoken_dict.keys():
                        response_dict["fund"] = self.fundtoken_dict[user_token]
                if InstanceID not in self.basketorder_push.keys():
                    self.basketorder_push[InstanceID] = {}
                if fund_key not in self.basketorder_push[InstanceID].keys():
                    self.basketorder_push[InstanceID][fund_key] = []
                self.basketorder_push[InstanceID][fund_key].append(response_dict)
    
    
    def handle_algorithm_push(self):
        for req_time, raw_response in self.algorithm_push_raw:
            response_json = json.loads(raw_response)
            response_dict = response_json["params"]
            response_dict["req_time"] = req_time
            action = response_dict["action"]
            InstanceID = response_dict["instructionid"]
            if InstanceID not in self.algorithm_push.keys():
                self.algorithm_push[InstanceID] = {}
            if action not in self.algorithm_push[InstanceID].keys():
                self.algorithm_push[InstanceID][action] = []
            self.algorithm_push[InstanceID][action].append(response_dict)

    
    # 资金查询
    def handle_fund_query(self):
        self.query_account_asset_dict = {}
        self.query_rzrq_account_asset_dict = {}
        self.query_ggt_account_asset_dict = {}
        self.query_asset_failed_list = []
        # 普通资金查询
        fund_reqlist = self.get_request_list("pb", "rpc.trader.stock", "query_account_asset")
        for key in fund_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
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
        # 信用资金查询
        rzrq_reqlist = self.get_request_list("json_funid", "stockrzrq", "501001")
        for key in rzrq_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
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
        # 港股通资金查询
        ggt_reqlist = self.get_request_list("json_funid", "stockths", "610013")
        for key in ggt_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
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
                    "type":"ggt",
                    "rsp_time":rsp_time,
                    "fund":fund,
                    "req_id":key,
                    "code":-1,
                    "message":"未返回资金查询结果"
                }
                self.query_asset_failed_list.append(result)
        # 返回查询fund_key
        fund_list = []
        for key, item in self.query_account_asset_dict.items():
            fund_list.append('%s|normal|%d' % (key, len(item)))
        for key, item in self.query_rzrq_account_asset_dict.items():
            fund_list.append('%s|rzrq|%d' % (key, len(item)))
        for key, item in self.query_ggt_account_asset_dict.items():
            fund_list.append('%s|ggt|%d' % (key, len(item)))
        return fund_list
    
    
    def show_fund_query(self, fund_key):
        query_type_dict = {
            "normal":self.query_account_asset_dict,
            "rzrq":self.query_rzrq_account_asset_dict,
            "ggt":self.query_ggt_account_asset_dict,
        }
        columns_query_type_dict = {
            "normal":["rsp_time", "available_value", "balance_value", "currency_msg",
                      "frozen_value", "market_value", "total_assets", "total_net_value"],
            "rzrq":["rsp_time", "EnableBalance", "AvailableValue", "AvailableMargin",
                    "FinEnableQuota", "SloEnableQuota", "FinCompactalance", "SloCompactBalance",
                    "FundAsset", "TotalAssets", "NetMoney", "WT_ZJ_JZC"],
            "ggt":["rsp_time", "TotalAssets", "AvailableValue", "GGT_SRZS", "GGT_ZTCZ","GGT_ZTRZ",
                   "GGT_SSCZ","GGT_SSRZ", "GGT_YSCZZJ", "GGT_HCJE","GGT_HRJE", "GGT_SYJE", "GGT_ZJKM", "GGT_SSZYJE"],
            "failed":["rsp_time", "fund", "req_id", "code", "message"],
        }
        rename_columns = {
            "normal":{},
            "rzrq":{
                "FinEnableQuota":"融资额度", "SloEnableQuota":"融券额度",
                "FinCompactalance":"融资负债","SloCompactBalance":"融券负债"
            },
            "ggt":{
                "GGT_SRZS":"上日总数",
                "GGT_ZTRZ":"在途入账",
                "GGT_ZTCZ":"在途出账",
                "GGT_SSRZ":"实时入账",
                "GGT_SSCZ":"实时出账",
                "GGT_YSCZZJ":"夜市出账资金",
                "GGT_HRJE":"划入金额",
                "GGT_HCJE":"划出金额",
                "GGT_SYJE":"剩余金额",
                "GGT_ZJKM":"资金科目",
                "GGT_SSZYJE":"实时占用金额",
            },
        }
        
        fund = fund_key.split('|')[0]
        query_type = fund_key.split('|')[1]
        query_data = query_type_dict[query_type][fund]
        
        print("\n查询账户", fund_key)
        
        df_query_data = pd.DataFrame(query_data, columns=columns_query_type_dict[query_type])
        print("\n查询成功请求数", len(query_data))
        df_query_data_renamed = df_query_data.rename(columns=rename_columns[query_type], inplace=True)
        display(df_query_data)
        
        query_data_failed = [item for item in self.query_asset_failed_list if (item["fund"] == fund and item["type"] == query_type)]
        df_failed = pd.DataFrame(query_data_failed, columns=columns_query_type_dict["failed"])
        print("\n查询失败请求数", len(query_data_failed))
        display(df_failed)


    # 持仓查询
    def handle_position_query(self):
        self.query_account_stock_dict = {}
        self.query_rzrq_account_stock_dict = {}
        self.query_ggt_account_stock_dict = {}
        self.query_stock_failed_list = []
        position_reqlist = self.get_request_list("pb", "rpc.trader.stock", "query_account_stock")
        for key in position_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_account_stock_dict.keys():
                self.query_account_stock_dict[fund] = {}
            if "error" not in response.keys():
                result = response["result"]["account_stock"]
                self.query_account_stock_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                self.query_stock_failed_list.append(result)
        position_reqlist = self.get_request_list("json_funid", "stockrzrq", "501002")
        for key in position_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_rzrq_account_stock_dict.keys():
                self.query_rzrq_account_stock_dict[fund] = {}
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    result = response["result"]["Array"]
                self.query_rzrq_account_stock_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "rzrq"
                self.query_stock_failed_list.append(result)
        position_reqlist = self.get_request_list("json_funid", "stockths", "610004")
        for key in position_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_ggt_account_stock_dict.keys():
                self.query_ggt_account_stock_dict[fund] = {}
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    result = response["result"]["Array"]
                self.query_ggt_account_stock_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "ggt"
                self.query_stock_failed_list.append(result)
        
        fundlist = []
        for fund, querytimedata in self.query_account_stock_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "normal", len(querytimedata)))
        for fund, querytimedata in self.query_rzrq_account_stock_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "rzrq", len(querytimedata)))
        for fund, querytimedata in self.query_ggt_account_stock_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "ggt", len(querytimedata)))
        return fundlist


    def get_position_querytime(self, fundkey):
        fund = fundkey.split("|")[0]
        querytype = fundkey.split("|")[1]
        self.position_querytime_reqid = {}
        typequerydict = {
            "normal":self.query_account_stock_dict,
            "rzrq":self.query_rzrq_account_stock_dict,
            "ggt":self.query_ggt_account_stock_dict,
        }
        querydatadict = typequerydict[querytype][fund]
        querytime_list = []
        for key, querydata in querydatadict.items():
            querytime = key.split("|")[0]
            reqid = key.split("|")[1]
            self.position_querytime_reqid[querytime] = reqid
            querytime_list.append("%s|%s" % (querytime,  len(querydata)))
        sorted_querytime_list = [item for item in sorted(querytime_list, key=lambda item: datetime.strptime(item.split('|')[0], '%Y%m%d %H:%M:%S.%f'), reverse=True)]
        return sorted_querytime_list
        
        
    def show_queryposition(self, account, querytime):
        fund = account.split("|")[0]
        querytype = account.split("|")[1]
        cnt = int(querytime.split("|")[1])
        querytime = querytime.split("|")[0]
        reqid = self.position_querytime_reqid[querytime]
        typequerydict = {
            "normal":self.query_account_stock_dict,
            "rzrq":self.query_rzrq_account_stock_dict,
            "ggt":self.query_ggt_account_stock_dict,
        }
        typecolumn = {
            "normal":['security_id', 'security_name', 'actual_amt', 'available_purchase_amt', 'available_stock_balance',
                'cost_price', 'frozen_qty', 'market', 'market_name', 'market_price', 'market_value', 'stock_balance', 'yield'],
            "rzrq":['SecurityID', 'SecurityName', 'AccountSecPosition', 'AvailableAmt', 'CostPrice', 'FrozenAmt', "Market",
                'MarketName', 'MarketPrice', 'MarketValue', 'StockBalance', 'Yield'],
            "ggt":['SecurityID', 'SecurityName', 'AvailableStockBalance', 'ActualAmt', 'StockBalance', 'FrozenQty',
                'CostPrice', "Market", 'MarketName', 'MarketPrice', 'MarketValue', 'Yield'],
        }
        typecolumnrename = {
            "normal":{"available_purchase_amt":"avail_purch", "available_stock_balance":"avail_amt","security_id":"security", "security_name":"symbol"},
            "rzrq":{"AccountSecPosition":"ActualAmt"},
            "ggt":{"SecurityID":"Security", "SecurityName":"Symbol", "AvailableStockBalance":"Available", "Market":"market", "MarketName":"Market"},
        }
        print("fund:", fund)
        print("querytype:", querytype)
        print("req_id:", reqid)
        if cnt == 0:
            print("本次持仓查询结果为空")
        else:
            querydata = typequerydict[querytype][fund]["%s|%s" % (querytime, reqid)]
            df_account_stock = pd.DataFrame(querydata, columns = typecolumn[querytype])
            df_account_stock.rename(columns = typecolumnrename[querytype], inplace=True)
            display(df_account_stock)
        
    
    # 委托查询
    def handle_order_query(self):
        self.query_order_dict = {}
        self.query_rzrq_order_dict = {}
        self.query_ggt_order_dict = {}
        self.query_order_failed_list = []
        order_reqlist = self.get_request_list("pb", "rpc.trader.stock", "query_order")
        for key in order_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_order_dict.keys():
                self.query_order_dict[fund] = {}
            if "error" not in response.keys():
                result = response["result"]["orders"]
                self.query_order_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                self.query_order_failed_list.append(result)
        # 适配调用500013查普通委托的情况
        order_reqlist = self.get_request_list("json_funid", "stockths", "500013")
        for key in order_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["UserToken"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_order_dict.keys():
                self.query_order_dict[fund] = {}
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    # 适配一下有Array返回 但是结果为None的情况
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_order_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                self.query_order_failed_list.append(result)
        order_reqlist = self.get_request_list("json_funid", "stockrzrq", "500013")
        for key in order_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_rzrq_order_dict.keys():
                self.query_rzrq_order_dict[fund] = {}
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    # 适配一下有Array返回 但是结果为None的情况
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_rzrq_order_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "rzrq"
                self.query_order_failed_list.append(result)
        order_reqlist = self.get_request_list("json_funid", "stockths", "610005")
        for key in order_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_ggt_order_dict.keys():
                self.query_ggt_order_dict[fund] = {}
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    # 适配一下有Array返回 但是结果为None的情况
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_ggt_order_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "ggt"
                self.query_order_failed_list.append(result)

        fundlist = []
        for fund, querytimedata in self.query_order_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "normal", len(querytimedata)))
        for fund, querytimedata in self.query_rzrq_order_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "rzrq", len(querytimedata)))
        for fund, querytimedata in self.query_ggt_order_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "ggt", len(querytimedata)))
        return fundlist
        
    
    def get_order_querytime(self, fundkey):
        fund = fundkey.split("|")[0]
        querytype = fundkey.split("|")[1]
        self.order_querytime_reqid = {}
        typequerydict = {
            "normal":self.query_order_dict,
            "rzrq":self.query_rzrq_order_dict,
            "ggt":self.query_ggt_order_dict,
        }
        querydatadict = typequerydict[querytype][fund]
        querytime_list = []
        for key, querydata in querydatadict.items():
            querytime = key.split("|")[0]
            reqid = key.split("|")[1]
            self.order_querytime_reqid[querytime] = reqid
            querytime_list.append("%s|%s" % (querytime,  len(querydata)))
        sorted_querytime_list = [item for item in sorted(querytime_list, key=lambda item: datetime.strptime(item.split('|')[0], '%Y%m%d %H:%M:%S.%f'), reverse=True)]
        return sorted_querytime_list
    
    
    def show_queryorder(self, account, querytime):
        fund = account.split("|")[0]
        querytype = account.split("|")[1]
        cnt = int(querytime.split("|")[1])
        querytime = querytime.split("|")[0]
        reqid = self.order_querytime_reqid[querytime]
        typequerydict = {
            "normal":self.query_order_dict,
            "rzrq":self.query_rzrq_order_dict,
            "ggt":self.query_ggt_order_dict,
        }
        typecolumn = {
            "normal":['insert_time', 'symbol', 'symbol_name', 'market_name', 'operation_msg', 'price','AvgPx','quantity', 'trade_amount', 
                'avg_price', 'order_no', 'order_status_msg', 'order_type_msg', 'currency', 'message',
                'OrderEntryTime', 'MarketName', 'Symbol', 'SecurityID', 'Price', 'OrderQty', 'Side', 'AvgPx', 'TradeVolume', 
                'OrderID', 'OperationMsg', 'Distribution', 'OrderStatusMsg', 'OrdType', 'OrderStatus2946'],
            "rzrq":['OrderEntryTime', 'MarketName', 'Symbol', 'SecurityID', 'Price', 'OrderQty', 'Side', 'AvgPx', 'TradeVolume', 
                'OrderID', 'OperationMsg', 'Distribution', 'OrderStatusMsg', 'OrdType', 'OrderStatus2946'],
            "ggt":['OrderTime', 'Market', 'MarketName', 'SecurityID', 'SecurityName', 'OrderPrice', 'OrderQty', 'Side', 'AvgPx',
                'TradeVolume', 'OrderID', 'OperationMsg', 'OrderStatusMsg'],
        }
        typecolumnrename = {
            "normal":{"symbol":"security", "symbol_name":"symbol", "trade_amount":"trade","order_status_msg":"status",
                "order_type_msg":"type", "avg_price":"avg","operation_msg":"op","market_name":"market"},
            "rzrq":{},
            "ggt":{"SecurityID":"Security", "SecurityName":"Symbol", "OrderPrice":"Price", "TradeVolume":"Volume"},
        }
        print("fund:", fund)
        print("querytype:", querytype)
        print("req_id:", reqid)
        if cnt == 0:
            print("本次委托查询结果为空")
        else:
            querydata = typequerydict[querytype][fund]["%s|%s" % (querytime, reqid)]
            df_queryorder = pd.DataFrame(querydata, columns = typecolumn[querytype])
            df_queryorder.rename(columns = typecolumnrename[querytype], inplace=True)
            df_queryorder = df_queryorder.dropna(axis=1, how='all')
            display(df_queryorder)
    
    
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
    
    
    # 成交查询
    def handle_trade_query(self):
        self.query_trade_dict = {}
        self.query_rzrq_trade_dict = {}
        self.query_ggt_trade_dict = {}
        self.query_trade_failed_list = []
        trade_reqlist = self.get_request_list("pb", "rpc.trader.stock", "query_trade")
        for key in trade_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_trade_dict.keys():
                self.query_trade_dict[fund] = {}
            if "error" not in response.keys():
                result = response["result"]["trades"]
                self.query_trade_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "normal"
                self.query_trade_failed_list.append(result)
        trade_reqlist = self.get_request_list("json_funid", "stockrzrq", "500014")
        for key in trade_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_rzrq_trade_dict.keys():
                self.query_rzrq_trade_dict[fund] = {}
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    # 适配一下有Array返回 但是结果为None的情况
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_rzrq_trade_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "rzrq"
                self.query_trade_failed_list.append(result)
        trade_reqlist = self.get_request_list("json_funid", "stockths", "610007")
        for key in trade_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_ggt_trade_dict.keys():
                self.query_ggt_trade_dict[fund] = {}
            if "error" not in response.keys():
                result = ""
                if "Array" in response["result"].keys():
                    # 适配一下有Array返回 但是结果为None的情况
                    arraydata = response["result"]["Array"]
                    if arraydata:
                        result = arraydata
                self.query_ggt_trade_dict[fund]["%s|%s" % (rsp_time, key)] = result
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                result["type"] = "ggt"
                self.query_trade_failed_list.append(result)

        fundlist = []
        for fund, querytimedata in self.query_trade_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "normal", len(querytimedata)))
        for fund, querytimedata in self.query_rzrq_trade_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "rzrq", len(querytimedata)))
        for fund, querytimedata in self.query_ggt_trade_dict.items():
            fundlist.append("%s|%s|%s" % (fund, "ggt", len(querytimedata)))
        return fundlist
    
    
    def get_trade_querytime(self, fundkey):
        fund = fundkey.split("|")[0]
        querytype = fundkey.split("|")[1]
        self.trade_querytime_reqid = {}
        typequerydict = {
            "normal":self.query_trade_dict,
            "rzrq":self.query_rzrq_trade_dict,
            "ggt":self.query_ggt_trade_dict,
        }
        querydatadict = typequerydict[querytype][fund]
        querytime_list = []
        for key, querydata in querydatadict.items():
            querytime = key.split("|")[0]
            reqid = key.split("|")[1]
            self.trade_querytime_reqid[querytime] = reqid
            querytime_list.append("%s|%s" % (querytime,  len(querydata)))
        sorted_querytime_list = [item for item in sorted(querytime_list, key=lambda item: datetime.strptime(item.split('|')[0], '%Y%m%d %H:%M:%S.%f'), reverse=True)]
        return sorted_querytime_list
    
    
    def show_querytrade(self, account, querytime, code):
        fund = account.split("|")[0]
        querytype = account.split("|")[1]
        cnt = int(querytime.split("|")[1])
        querytime = querytime.split("|")[0]
        reqid = self.trade_querytime_reqid[querytime]
        typequerydict = {
            "normal":self.query_trade_dict,
            "rzrq":self.query_rzrq_trade_dict,
            "ggt":self.query_ggt_trade_dict,
        }
        typecolumn = {
            "normal":['trade_time', 'order_no', 'symbol', 'symbol_name', 'market_name', 'price', 'quantity', 'trade_amount', 
                'order_type_msg', 'operation_msg', 'currency', 'currency_msg', "shareholder_account", 'message'],
            "rzrq":['TransactTime', 'MarketName', 'Symbol', 'SecurityID', 'Price', 'OperationMsg', 'Side', 'AvgPx', 'BusinessAmount', 
                'GrossTradeAmt', 'OrderID', 'OrdType', 'TradeVolume', 'OrderStatus', 'OperationMsg', 'Distribution'],
            "ggt":['TransactTime', 'MarketName', 'SecurityID', 'SecurityName', 'Price', 'OperationMsg', 'Side', 'AvgPx', 
                'BusinessAmount', 'GrossTradeAmt', 'OrderID', 'OrdType', 'TradeVolume', 'TradeStatus', 'Distribution'],
        }
        typecolumnrename = {
            "normal":{"symbol":"SecurityID", "symbol_name":"Symbol", "trade_amount":"trade", "order_type_msg":"type", 
                "operation_msg":"op", "market_name":"market", "currency_msg":"currency2", "shareholder_account":"gdzh"},
            "rzrq":{},
            "ggt":{"SecurityName":"Symbol"},
        }
        print("fund:", fund)
        print("querytype:", querytype)
        print("req_id:", reqid)
        print("filter_stockcode:", code)
        if cnt == 0:
            print("本次成交查询结果为空")
        else:
            querydata = typequerydict[querytype][fund]["%s|%s" % (querytime, reqid)]
            df_querytrade = pd.DataFrame(querydata, columns = typecolumn[querytype])
            df_querytrade.rename(columns = typecolumnrename[querytype], inplace=True)
            df_querytrade = df_querytrade.dropna(axis=1, how='all')
            if code != "":
                df = df_querytrade[df_querytrade["SecurityID"] == code]
                display(df)
            else:
                display(df_querytrade)
    
    
    def show_querytrade_summary(self, account):
        fund = account.split("|")[0]
        querytype = account.split("|")[1]
        typequerydict = {
            "normal":self.query_trade_dict,
            "rzrq":self.query_rzrq_trade_dict,
            "ggt":self.query_ggt_trade_dict,
        }
        print("\n统计单账户查询请求返回行数")
        print("查询账号：", account, '\n')
        for query_time, querydata in typequerydict[querytype][fund].items():
            print(query_time, len(querydata))
    
    
    def show_querytrade_all(self):
        print("\n根据时间统计查询行数\n")
        column_index = set()
        row_index = set()
        typequerydict = {
            "normal":self.query_trade_dict,
            "rzrq":self.query_rzrq_trade_dict,
            "ggt":self.query_ggt_trade_dict,
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
    
    
    # 新股申购
    def handle_xgsg_query(self):
        self.xgsg_query_list = []
        for protocol, service, funid in [("json_funid", "stockths", "503002"), ("json_funid", "stockrzrq", "501022")]:
            req_list = self.get_request_list(protocol, service, funid)
            for key in req_list:
                item = self.req_pairs[key]
                request = item["request"]
                response = item["response"]
                req_time = item["req_time"]
                rsp_time = item["rsp_time"]
                fund_token = request["params"]["UserToken"]
                query = {"rsp_time":rsp_time, "req_id":key, "funid":funid, "fund":self.get_fund_by_fund_token(fund_token)}
                if "result" not in response:
                    query["message"] = response["error"]["message"]
                else:
                    if "Array" in response["result"]:
                        querydata = response["result"]["Array"]
                        try:
                            for item in querydata:
                                market = item["MarketName"]
                                marketid = str(item["Market"])
                                available = item["AvailableStockBalance"]
                                marketname = '%s|%s' % (str(marketid), str(market))
                                query["["+marketname+"]额度"] = available
                        except Exception as e:
                            query["message"] = "返回结果异常：" + str(e)
                    else:
                        query["message"] = "未返回查询结果"
                self.xgsg_query_list.append(query)
        
        fund_list = list(set([item["fund"] for item in self.xgsg_query_list]))
        fund_list.insert(0, "全部")
        return fund_list
        
        
    def show_xgsg_query(self, fund="全部", show_summary=False):
        bFilter = True
        if fund == "全部":
            bFilter = False
            if not show_summary:
                print("显示全部账户新股申购配售额度信息")
        else:
            print("显示账户[%s]新股申购配售额度信息" % fund)
        unique_fund_list = list(set([item["fund"] for item in self.xgsg_query_list]))
        list_summary = []
        # 如果是全部账户，那么不筛选；否则展示筛选的账号
        for fund_key in unique_fund_list:
            if show_summary:
                querydata = [item for item in self.xgsg_query_list if item["fund"] == fund_key]
                list_summary.append({"fund":fund_key, "query":len(querydata)})
            else:
                if not bFilter or (bFilter and (fund in fund_key)):
                    print('\n')
                    querydata = [item for item in self.xgsg_query_list if item["fund"] == fund_key]
                    print(fund_key, len(querydata))
                    display(pd.DataFrame(querydata))
        if show_summary:
            display(pd.DataFrame(list_summary).sort_values(by="fund"))
    
    
    def handle_zqmx_query(self):
        self.zqmx_query_list = []
        for protocol, service, funid in [("json_funid", "stockths", "503003"), ("json_funid", "stockrzrq", "501023")]:
            req_list = self.get_request_list(protocol, service, funid)
            for key in req_list:
                item = self.req_pairs[key]
                request = item["request"]
                response = item["response"]
                req_time = item["req_time"]
                rsp_time = item["rsp_time"]
                fund_token = request["params"]["UserToken"]
                query = {"rsp_time":rsp_time, "req_id":key, "funid":funid, "fund":self.get_fund_by_fund_token(fund_token)}
                if "result" not in response:
                    query["message"] = response["error"]["message"]
                else:
                    if "Array" in response["result"]:
                        querydata = response["result"]["Array"]
                        try:
                            for item in querydata:
                                market = item["MarketName"]
                                marketid = str(item["Market"])
                                available = item["AvailableStockBalance"]
                                marketname = '%s|%s' % (str(marketid), str(market))
                                query["["+marketname+"]额度"] = available
                        except Exception as e:
                            query["message"] = "返回结果异常：" + str(e)
                    else:
                        query["message"] = "未返回查询结果"
                self.zqmx_query_list.append(query)
        
        fund_list = list(set([item["fund"] for item in self.zqmx_query_list]))
        fund_list.insert(0, "全部")
        return fund_list
    
    
    def show_zqmx_query(self, fund="全部", show_summary=False):
        bFilter = True
        if fund == "全部":
            bFilter = False
            if not show_summary:
                print("显示全部账户新股中签明细信息")
        else:
            print("显示账户[%s]新股中签明细信息" % fund)
        unique_fund_list = list(set([item["fund"] for item in self.zqmx_query_list]))
        list_summary = []
        # 如果是全部账户，那么不筛选；否则展示筛选的账号
        for fund_key in unique_fund_list:
            if show_summary:
                querydata = [item for item in self.zqmx_query_list if item["fund"] == fund_key]
                list_summary.append({"fund":fund_key, "query":len(querydata)})
            else:
                if not bFilter or (bFilter and (fund in fund_key)):
                    print('\n')
                    querydata = [item for item in self.zqmx_query_list if item["fund"] == fund_key]
                    print(fund_key, len(querydata))
                    display(pd.DataFrame(querydata))
        if show_summary:
            display(pd.DataFrame(list_summary).sort_values(by="fund"))
    
    
    # 融资融券
    def handle_finable_security_query(self):
        self.query_finable_security_dict = {}
        self.query_finable_security_failed = []
        self.finable_querytime_reqid = {}
        rzrq_reqlist = self.get_request_list("json_funid", "stockrzrq", "501005")
        for key in rzrq_reqlist:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            fund_token = request["params"]["fund_token"]
            fund = self.get_fund_by_fund_token(fund_token)
            if fund not in self.query_finable_security_dict.keys():
                self.query_finable_security_dict[fund] = {}
            if "error" not in response.keys():
                if "Array" in response["result"].keys():
                    result = response["result"]["Array"]
                    self.finable_querytime_reqid[rsp_time] = key
                    self.query_finable_security_dict[fund]["%s|%d" % (rsp_time, len(result))] = result
                else:
                    self.query_finable_security_failed.append({
                        "fund":fund,
                        "rsp_time":rsp_time,
                        "req_id":key,
                        "message":"result返回结果中没有Array",
                    })
            else:
                result = response["error"]
                result["fund_token"] = fund_token
                result["fund"] = fund
                result["rsp_time"] = rsp_time
                result["req_id"] = key
                self.query_finable_security_failed.append(result)
        fundlist = [key for key in self.query_finable_security_dict]
        return fundlist


    def get_finable_security_querytime(self, fundkey):
        querydatadict = self.query_finable_security_dict[fundkey]
        querytime_list = []
        for key, querydata in querydatadict.items():
            querytime = key.split("|")[0]
            querytime_list.append(key)
        sorted_querytime_list = [item for item in sorted(querytime_list, key=lambda item: datetime.strptime(item.split('|')[0], '%Y%m%d %H:%M:%S.%f'), reverse=True)]
        if len(sorted_querytime_list) == 0:
            sorted_querytime_list.append("空")
        sorted_querytime_list


    def show_finable_security(self, fund_key, query_time, show_securities=False, stock_code=""):
        self.finable_security_dict = {}
        if query_time != "空":
            querytime = query_time.split('|')[0]
            reqid = self.finable_querytime_reqid[querytime]
            print("查询账户", fund_key)
            print("查询时间", querytime)
            print("req_id", reqid, '\n')
            if stock_code == "":
                query_data = self.query_finable_security_dict[fund_key][query_time]
                for data in query_data:
                    market = data["MarketID"]
                    security = data["SecurityID"]
                    market_name = data["MarketName"]
                    index = '%s:%s' % (market_name, market)
                    if index not in self.finable_security_dict.keys():
                        self.finable_security_dict[index] = []
                    self.finable_security_dict[index].append(security)
                # 直接展示各市场的股票列表
                for index, security_list in self.finable_security_dict.items():
                    print(index, "股票数：" + str(len(security_list)))
                    if show_securities:
                        print(security_list)
            else:
                is_finded = False
                query_data = self.query_finable_security_dict[fund_key][query_time]
                for data in query_data:
                    market = data["MarketID"]
                    security = data["SecurityID"]
                    if security == stock_code:
                        # 只展示个股
                        display(data)
                        is_finded = True
                if not is_finded:
                    print("证券代码 %s 不在可融资股票列表之中" % stock_code)
        df = pd.DataFrame(self.query_finable_security_failed, columns=["rsp_time", "fund", "req_id", "code", "message"])
        df = df[df["fund"] == fund_key]
        print("\n失败查询请求", fund_key)
        display(df)
    
    
    # 多户交易/篮子交易/篮子算法
    def handle_basketorder(self):
        print("单户/多户交易数据分析中...")
        self.singleorder_list = []
        self.singleorder_cancellist = []
        self.basketorder_list = []
        self.basketorder_op_list = []
        self.basketorder_detail_dict = {}
        """
            instanceid = {
                "req_id" : "",
                order_list : {
                    "symbol" : [],
                }
            }
        """
        self.basketorder_info = {}
        # 单户交易
        req_list = self.get_request_list("pb", "rpc.order.manager", "insert_order_jgb")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            handledata = request["params"]
            if "result" in response.keys():
                handledata["code"] = response["result"]["code"]
            else:
                handledata["code"] = response["error"]["code"]
                handledata["message"] = response["error"]["message"]
            handledata["rsp_time"] = rsp_time
            handledata["req_id"] = key
            handledata["fund"] = self.get_fund_by_fund_token(request["params"]["fund_token"])
            self.singleorder_list.append(handledata)
        # 单户撤单
        req_list = self.get_request_list("pb", "rpc.order.manager", "cancel_order_jgb")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            handledata = request["params"]
            if "result" in response.keys():
                handledata["code"] = response["result"]["code"]
            else:
                handledata["code"] = response["error"]["code"]
                handledata["message"] = response["error"]["message"]
            handledata["rsp_time"] = rsp_time
            handledata["fund"] = self.get_fund_by_fund_token(request["params"]["fund_token"])
            self.singleorder_cancellist.append(handledata)
        # 多户交易
        req_list = self.get_request_list("json", "basket", "BasketOrder")
        # 增加篮子算法的请求
        [req_list.append(key) for key in self.get_request_list("json", "basket", "InstructionOrder")]
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            instanceid = request["params"]["InstanceID"]
            result = {
                "rsp_time":rsp_time,
                "instanceid":request["params"]["InstanceID"],
                "source":request["params"]["ClientOrderType"],
                "fund_num":0,
                "security_num":0,
                "side":request["params"]["Side"],
                "note":request["params"]["Note"],
            }
            if instanceid not in self.basketorder_info.keys():
                self.basketorder_info[instanceid] = {"req_id":key, "order_list":{}}
            basketorder_detail = request["params"]["OrderBase"]
            security_list = set([item["SecurityID"] for item in basketorder_detail])
            str_security = ','.join(security_list)
            result["security_num"] = len(security_list)
            fund_list = set([self.get_fund_by_fund_token(item["fund_token"]) for item in basketorder_detail])
            str_fund = ','.join(fund_list)
            result["fund_num"] = len(fund_list)
            self.basketorder_list.append(result)
            for item in basketorder_detail:
                item["fund"] = self.get_fund_by_fund_token(item["fund_token"])
                self.basketorder_detail_dict[instanceid] = basketorder_detail
        # 多户撤单/撤补
        req_list = self.get_request_list("json", "basket", "OrderAction")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            handledata = request["params"]
            handledata["rsp_time"] = rsp_time
            handledata["result"] = response["result"]["code"]
            self.basketorder_op_list.append(handledata)
        # 篮子算法单 待处理
        
        # 返回订单来源类型，方便筛选
        source_list = list(set([item["source"] for item in self.basketorder_list]))
        source_list.insert(0, "全部")
        return source_list


    def show_basket_summary(self, source="全部", fund="", stockcode="", showorders=False):
        # 展示篮子订单情况
        # 只有未筛选fund、stockcode时，展示单户情况
        if source == "全部" and fund == "" and stockcode == "":
            print("\n当日新增单户委托情况 insert_order_jgb")
            print("委托成功请求")
            df_singleorder = pd.DataFrame(self.singleorder_list, columns=self.columns["singleorder"])
            df_singleorder_success = df_singleorder[df_singleorder["code"] == 0]
            display(df_singleorder_success)
            print("委托失败请求")
            print("error message")
            df_singleorder = pd.DataFrame(self.singleorder_list, columns=self.columns["singleorder_failed"])
            df_singleorder_failed = df_singleorder[df_singleorder["code"] != 0]
            message_list = [item["message"] for item in self.singleorder_list if item["code"] != 0]
            display(message_list)
            display(df_singleorder_failed)
            print("\n当日单户委托撤单情况 cancel_order_jgb")
            df_singleorder_cancel = pd.DataFrame(self.singleorder_cancellist, columns=self.columns["singleorder_cancel"])
            display(df_singleorder_cancel)
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
        # 展示筛选后的母单信息
        if fund != "" or stockcode != "":
            print("订单来源:", source)
            print("资金账号:", fund)
            print("证券代码:", stockcode)
        security_list = []
        for instanceid in filtered_instanceid:
            for item in self.basketorder_detail_dict[instanceid]:
                security_list.append(item["SecurityID"])
        distinct_security_list = list(set(security_list))
        print("\n涉及的多户交易股票列表", len(distinct_security_list), distinct_security_list)
        print("\n当日新增篮子单情况 BasketOrder")
        df_basketorder = pd.DataFrame(filtered_basketorder)
        display(df_basketorder)
        print("\n当日篮子单操作情况 OrderAction")
        filted_op_list = [item for item in self.basketorder_op_list if item["InstanceID"] in filtered_instanceid]
        df_basketorder_op = pd.DataFrame(filted_op_list, columns=self.columns["basketorder_cancel"])
        display(df_basketorder_op)
        print("\n篮子单总推送数:%d" % len(self.basketorder_push_raw))
        # 根据最后一个配置项判断是否展示详细子单，当筛选条件都为空时，则不展示详细子单
        if showorders:
            if fund == "" and stockcode == "":
                print("没有筛选条件[资金账号]或者[证券代码], 不展示子单详细信息")
            else:
                for instanceid in filtered_instanceid:
                    self.show_basket_order_detail(instanceid, fund, stockcode)


    def get_basketorder_code(self):
        security_list = []
        for key, detail in self.basketorder_detail_dict.items():
            for item in detail:
                security_list.append(item["SecurityID"])
        distinct_security_list = list(set(security_list))
        return distinct_security_list


    def show_basket_instance_detail(self, instanceid, fund="", stockcode=""):
        if instanceid == "":
            print("\n母单[%s]不在当日新建篮子列表中" % instanceid)
        else:
            print("\n母单参数详情", instanceid)
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
            display(pd.DataFrame(list_the_create))
            print("\n母单OrderBase")
            display(pd.DataFrame(self.basketorder_detail_dict[instanceid], 
                columns=["fund", "SecurityID", "Side", "OrderQty", "OrderPrice", "MarketID", "PriceType"]))
    
    
    def show_basket_order_detail(self, instanceid, fund="", stockcode=""):
        print("*"*120)
        print("\n母单[%s]的全部子单详情" % instanceid)
        for fund_key, pushdata in self.basketorder_push[instanceid].items():
            fund_token = fund_key.split("|")[0]
            fundinfo = self.get_fund_by_fund_token(fund_token)
            if fund == "" or (fund != "" and fund in fundinfo):
                print("\n子单详情 fund:%s, fund_token:%s, 推送数:%d" % (fundinfo, fund_token, len(pushdata)))
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
                print("text_list", list(set(df_basketorder_push["Text"].tolist())))
                display(df_basketorder_push)
    
    
    def get_basketorder_detail(self, instanceid):
        if instanceid in self.basketorder_detail_dict.keys():
            basketorder_detail = self.basketorder_detail_dict[instanceid]
            df_basketorder_detail = pd.DataFrame(basketorder_detail, columns = [
                "fund_token", "fund", "SecurityID", "MarketID", "Side", "OrderQty", "OrderPrice", "PriceType"
            ])
            return df_basketorder_detail


    def get_basketorder_push_detail(self, instanceid, fund_key):
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
        self.basketorder_query_dict = {}
        req_list = self.get_request_list("json", "basket", "QryBasketOrder")
        for key in req_list:
            value = self.req_pairs[key]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            querydata = response["result"]
            self.basketorder_query_dict["%s|%d|%s" % (rsp_time, len(querydata), key)] = querydata
        querytime_list = list(self.basketorder_query_dict.keys())
        return querytime_list
        
        
    def show_basket_query(self, querytime):
        req_id = querytime.split('|')[2]
        querydata = self.basketorder_query_dict[querytime]
        print("本次查询req_id", req_id)
        if len(querydata) > 0:
            df_querydata = pd.DataFrame(querydata, columns=["CreateDate", "CreateTime", "InstanceID", "ClientOrderType",  "OrderQty", "DealVolume", "CancelOrderQty", "OperationMsg","Text"])
            df_querydata_sorted = df_querydata.sort_values(by="CreateTime", ascending=True)
            instance_list = list(set(df_querydata["InstanceID"].to_list()))
            display(df_querydata_sorted)
        else:
            print("本次篮子单查询结果为空")
        
        
    def show_basket_initreqs(self, instance, isfullreqs=False):
        req_id = ""
        if instance in self.req_pairs.keys():
            req_id = instance
        if instance in self.basketorder_info.keys():
            req_id = self.basketorder_info[instance]["req_id"]
        if req_id != "":
            self.show_request_and_response(req_id, isfullreqs)
        else:
            print("找不到id[%s]关联的原始请求信息" % instance)
    

    # 算法交易
    def handle_algorithm(self):
        self.algorithm_list = []
        self.algorithm_detail_dcit = {}
        self.algorithm_query_dict = {}
        self.query_algorithm_df = {}
        for key, value in self.req_pairs.items():
            protocol = value["protocol"]
            request = value["request"]
            response = value["response"]
            req_time = value["req_time"]
            rsp_time = value["rsp_time"]
            len_req = len(json.dumps(request))
            len_rsp = len(json.dumps(response))
            if len_req != 2 and len_rsp != 2:
                if protocol == "json":
                    if request["method"] == "new_instmanage":
                        dict_inst_type = ["普通","条件单","算法单"]
                        dict_init_desc = ["启动","暂停"]
                        dict_expire_desc = ["撤单","不撤"]
                        dict_special_desc = ["跟限价委托", "不委托"]
                        action = request["params"]["action"]
                        # 过滤 instructionid在请求参数中的情况
                        if action == "query" and "instructionid" not in request["params"].keys():
                            query_data = response["result"]["instructions"]
                            format_query_data = []
                            for item in query_data:
                                instanceid = item["instructionid"]
                                fund = ""
                                fund_token = item["fund_token"]
                                if fund_token in self.client_fundtoken_mapping.keys():
                                    if self.client_fundtoken_mapping[fund_token] in self.fundtoken_dict.keys():
                                        fund = self.fundtoken_dict[self.client_fundtoken_mapping[item["fund_token"]]]
                                format_query_data.append({
                                    "rsp_time":rsp_time,
                                    "fund":fund,
                                    "inst_id":instanceid,
                                    "inst_type":dict_inst_type[item["instructiontype"]],  # 0-普通, 1-条件, 2-算法
                                    "algorithm":item["instructionparam"]["algorithmtype"],
                                    "security":item["security"],
                                    "side":item["side"],
                                    "总数":item["qty"],
                                    "剩余":item["qtyleft"],
                                    "成交":item["qtytrade"],
                                    "撤销":item["qtycancel"],
                                    # "price":item["price"],
                                    # "ptype":item["pricetype"],
                                    # "pimit":item["pricelimit"],
                                    # "到期后":dict_expire_desc[item["expirerevokeflag"]],  # 1-算法到期后撤单, 0-算法到期后不撤单
                                    "状态":item["statusmsg"],
                                    # "msg":item["msg"],
                                })
                            self.algorithm_query_dict[rsp_time] = format_query_data
                            df_algorithm = ""
                            if len(format_query_data) > 0:
                                df_algorithm = pd.DataFrame(format_query_data)
                            query_index = rsp_time + "|" + str(len(format_query_data))
                            self.query_algorithm_df[query_index] = df_algorithm
                        if action == "new":
                            instanceid = response["result"]["instructionid"]
                            fundtoken = request["params"]["fund_token"]
                            fund = ""
                            if fundtoken in self.fundtoken_dict.keys():
                                fund = self.fundtoken_dict[fundtoken]
                            new_algorithm = {
                                "rsp_time":rsp_time,
                                "fund":fund,
                                "inst_id":instanceid,
                                "inst_type":dict_inst_type[request["params"]["instructiontype"]],  # 0-普通, 1-条件, 2-算法
                                "security":request["params"]["security"],
                                "side":request["params"]["side"],
                                "qty":request["params"]["qty"],
                                "price":request["params"]["price"],
                                "ptype":request["params"]["pricetype"],
                                "pimit":request["params"]["pricelimit"],
                                "创建后":dict_init_desc[request["params"]["initflag"]],  # 0-创建后立即启动, 1-创建后暂停
                                "到期后":dict_expire_desc[request["params"]["expirerevokeflag"]],  # 1-算法到期后撤单, 0-算法到期后不撤单
                                "取价失败后":dict_special_desc[request["params"]["specialdeal"]],    # 1-勾选价格为空时不委托, 0-取不到行情时，取跟限价委托
                            }
                            self.algorithm_list.append(new_algorithm)
                            dict_eop_desc = ["忽略","暂停","废单"]
                            dict_expre2_desc = ["不继续委托", "继续委托"]
                            algorithm_params = request["params"]["instructionparam"]["algorithm"]
                            new_algorithm_detail = {
                                "algorithm":request["params"]["instructionparam"]["algorithmtype"],
                                "交易失败":dict_eop_desc[request["params"]["instructionparam"]["tradeerrop"]],
                                "到期后":dict_expre2_desc[request["params"]["instructionparam"]["tradeexpireoperation"]],
                            }
                            new_algorithm_detail.update({k:v for k, v in algorithm_params.items() if v is not None})
                            new_algorithm_detail["starttime"] = datetime.fromtimestamp(new_algorithm_detail["starttime"]).strftime("%Y-%m-%d %H:%M:%S")
                            new_algorithm_detail["endtime"] = datetime.fromtimestamp(new_algorithm_detail["endtime"]).strftime("%Y-%m-%d %H:%M:%S")
                            if "needreprice" in new_algorithm_detail.keys():
                                if new_algorithm_detail["needreprice"] != "1":
                                    new_algorithm_detail.pop("repricetype", None)
                                    new_algorithm_detail.pop("reprice", None)
                            if "pricelimittype" not in new_algorithm_detail.keys():
                                new_algorithm_detail.pop("pricefloatuplimit", None)
                                new_algorithm_detail.pop("pricefloatdownlimit", None)
                                new_algorithm_detail.pop("priceuplimit", None)
                                new_algorithm_detail.pop("pricedownlimit", None)
                            new_algorithm_detail.pop("timelimit", None)
                            self.algorithm_detail_dcit[instanceid] = new_algorithm_detail
        
        df_algorithm = pd.DataFrame(self.algorithm_list)
        return df_algorithm


    def get_algorithm_code(self):
        security_list = []
        for algorithm in self.algorithm_list:
            security_list.append(algorithm["security"])
        distinct_security_list = list(set(security_list))
        return distinct_security_list


    def get_algorithm_detail(self, instanceid):
        if instanceid in self.algorithm_detail_dcit.keys():
            algorithm_detail = self.algorithm_detail_dcit[instanceid]
            # 算法单详情是个dict, 需要转化成list才能格式化
            df_algorithm_detail = pd.DataFrame([algorithm_detail])
            df_algorithm_detail.rename(columns = {
                "revokeinterval":"补单间隔","rechaseinterval":"补单间隔","minordernumber":"最小子单","maxordernumber":"最大子单",
                "slicetime":"委托间隔","timerand":"随机委托", "randprice":"随机价浮",
                "pricelimittype":"限价类型","pricefloatuplimit":"限价上限","pricefloatdownlimit":"限价下限",
                "needreprice":"补单","entrustlimit":"委托次数限制","startfloat":"浮动启动笔数",
            }, inplace=True)
            return df_algorithm_detail


    def get_algorithm_push_detail(self, instanceid, push_type):
        dict_pushtype_keep_columns = {
            "instruction":["req_time", "avgpx", "qty", "qtyleft", "qtycancel", "qtytrade", "statusmsg", "msg"],
            "order":["req_time", "orderid", "operationmsg", "avgpx", "price", "qty", "qtyleft", "qtycancel", "qtytrade", "statusmsg", "msg"],
        }
        push_key = next((k for k in self.algorithm_push[instanceid] if push_type in k), None)
        push_data = self.algorithm_push[instanceid][push_key]
        df_algorithm_push = pd.DataFrame(push_data, columns = dict_pushtype_keep_columns[push_type])
        return push_key, df_algorithm_push


    def show_queryalgorithm(self, querytime):
        df_query_algorithm = self.query_algorithm_df[querytime]
        if isinstance(df_query_algorithm, pd.DataFrame) and not df_query_algorithm.empty:
            display(df_query_algorithm)
        else:
            print("本次查询算法单结果为空")


    # 条件交易
    def handle_condition(self):
        print("条件单数据分析中...")
        # 新建组合条件单
        self.gradecondition_create = []
        # 母单关联的操作详情，包含：请求id，下单参数详情，后续操作情况
        """
        {
            "order_no":{
                "req_id":"",
                "instruction_params":{},
                "operations":[],
            }
        }
        """
        self.gradecondition_info = {}
        """
        {
            "order_no":{
                "grade_instruction":[],
                "grade_condition":{
                    "symbol":[],
                },
                "grade_order":{
                    "symbol":[],
                },
            }
        }
        """
        self.gradecondition_push = {}
        # 处理条件单 rpc.condition 暂缺
        
        
        # 处理组合条件单/狙击涨停 rpc.gradecondition
        # 1、新建母单 返回 order_no
        # json/rpc.gradecondition/create_gradecondition
        req_list = self.get_request_list("json", "rpc.gradecondition", "create_gradecondition")
        for key in req_list:
            item = self.req_pairs[key]
            request = item["request"]
            response = item["response"]
            req_time = item["req_time"]
            rsp_time = item["rsp_time"]
            requestdata = request["params"]
            requestdata["rsp_time"] = rsp_time
            order_no = response["result"]["order_no"]
            if order_no not in self.gradecondition_info.keys():
                self.gradecondition_info[order_no] = {"req_id":key, "instruction_params":[], "operations":[]}
            requestdata["order_no"] = order_no
            # 如果母单中有 fund_token, 那么转化
            if "fund_token" in request["params"].keys():
                requestdata["fund"] = self.get_fund_by_fund_token(request["params"]["fund_token"])
            self.gradecondition_create.append(requestdata)
            # 如果子单中有fund_token，那么转化
            if "instruction_param" in request["params"].keys():
                instruction_param = request["params"]["instruction_param"]
                for instruction in instruction_param:
                    if "fund_token" in instruction.keys():
                        instruction["fund"] = self.fundtoken_dict[instruction["fund_token"]]
                self.gradecondition_info[order_no]["instruction_params"] = instruction_param

        # 2、母单操作 order_no
        operation_cmd = ["delete_gradecondition", "pause_gradecondition", "modify_gradecondition", "activate_gradecondition", "cancel_gradecondition"]
        for action in operation_cmd:
            operation_reqs = self.get_request_list("json", "rpc.gradecondition", action)
            for request_key in operation_reqs:
                operation_req = self.req_pairs[request_key]
                request = operation_req["request"]["params"]
                response = {}
                if "result" in operation_req["response"].keys():
                    response = operation_req["response"]["result"]
                else:
                    response = operation_req["response"]["error"]
                    response["msg"] = response["message"]
                rsp_time = operation_req["rsp_time"]
                order_no = request["order_no"]
                if order_no not in self.gradecondition_info.keys():
                    self.gradecondition_info[order_no] = {"req_id":"", "instruction_params":[], "operations":[]}
                request["id"] = operation_req["request"]["id"]
                merged_dict = {**{f"request_{k}" if (k in response and v != response[k]) else k: v for k, v in request.items()},
                               **{f"response_{k}"if (k in request and v != request[k]) else k: v  for k, v in response.items()}}
                merged_dict["rsp_time"] = rsp_time
                self.gradecondition_info[order_no]["operations"].append(merged_dict)
        # 3、母单下的子单操作
        
        # 4、推送
        for rsp_time, rsp_data in self.gradecondition_push_instruction:
            pushdata = json.loads(rsp_data)["params"]
            pushdata["rsp_time"] = rsp_time
            order_no = pushdata["order_no"]
            if order_no not in self.gradecondition_push.keys():
                self.gradecondition_push[order_no] = {"grade_instruction":[],"grade_condition":{},"grade_order":{}}
            self.gradecondition_push[order_no]["grade_instruction"].append(pushdata)
        for rsp_time, rsp_data in self.gradecondition_push_condition:
            pushdata = json.loads(rsp_data)["params"]
            pushdata["rsp_time"] = rsp_time
            order_no = pushdata["order_no"]
            symbol = pushdata["symbol"]
            if order_no not in self.gradecondition_push.keys():
                self.gradecondition_push[order_no] = {"grade_instruction":[],"grade_condition":{},"grade_order":{}}
            if symbol not in self.gradecondition_push[order_no]["grade_condition"].keys():
                self.gradecondition_push[order_no]["grade_condition"][symbol] = []
            self.gradecondition_push[order_no]["grade_condition"][symbol].append(pushdata)
        for rsp_time, rsp_data in self.gradecondition_push_order:
            pushdata = json.loads(rsp_data)["params"]
            order_no = pushdata["order_no"]
            symbol = pushdata["data"]["SecurityID"]
            orderdata = pushdata["data"]
            orderdata["rsp_time"] = rsp_time
            if order_no not in self.gradecondition_push.keys():
                self.gradecondition_push[order_no] = {"grade_instruction":[],"grade_condition":{},"grade_order":{}}
            if symbol not in self.gradecondition_push[order_no]["grade_order"].keys():
                self.gradecondition_push[order_no]["grade_order"][symbol] = []
            self.gradecondition_push[order_no]["grade_order"][symbol].append(orderdata)
    
    
    def show_condition_summary(self):
        # print("新增条件单情况：暂缺")
        df_gradecondition_create = pd.DataFrame(self.gradecondition_create, columns=self.columns["gradecondition_create"])
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
        df_gradecondition_operations = pd.DataFrame(gradecondition_operations, columns=self.columns["gradecondition_operate"])
        df_gradecondition_operations = df_gradecondition_operations.sort_values(by='rsp_time', ascending=True).dropna(axis=1, how="all")
        if len(gradecondition_operations) > 0:
            df_gradecondition_operations["action"] = df_gradecondition_operations["action"].apply(lambda x: x.split('_')[0])
        display(df_gradecondition_operations)
        print("母单推送数:%d, 子单推送数:%d, 子单委托推送数:%d" % (
            len(self.gradecondition_push_instruction), 
            len(self.gradecondition_push_condition),
            len(self.gradecondition_push_order)))
    
    
    def show_condition_instance_detail(self, order_no, fund, security):
        if order_no not in self.gradecondition_info.keys():
            print("母单[%s]不在新建母单列表中" % order_no)
        else:
            # 母单创建信息
            print("母单创建详情", order_no)
            the_create = next((item for item in self.gradecondition_create if item["order_no"] == order_no))
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
                if key in dict_key_2_note.keys():
                    return dict_key_2_note[key]
                return note
            
            for key, value in the_create.items():
                value_format = value
                if key == "note":
                    condition_text = value
                if type(value) in (dict, list):
                    value_format = "valuetype is %s, len=%d" % (str(type(value)), len(value))
                list_the_create.append({"请求字段":key, "字段解释":get_key_note(key), "值":value_format})
            print("condition_text", condition_text)
            with pd.option_context("display.max_colwidth", 100, "display.width", 200):
                display(pd.DataFrame(list_the_create))
            # 母单操作
            print("\n当日母单操作")
            operations = self.gradecondition_info[order_no]["operations"]
            df_gradecondition_operations = pd.DataFrame(operations, columns=self.columns["gradecondition_operate"])
            df_gradecondition_operations = df_gradecondition_operations.sort_values(by='rsp_time', ascending=True).dropna(axis=1, how="all")
            if len(operations) > 0:
                df_gradecondition_operations["action"] = df_gradecondition_operations["action"].apply(lambda x: x.split('_')[0])
            display(df_gradecondition_operations)
            # 增加母单改单前后的信息对比
            modify_information = []
            modify_information.append(the_create)
            operations = self.gradecondition_info[order_no]["operations"]
            for operation in operations:
                action = operation["action"]
                req_id = operation["id"]
                if action == "modify_gradecondition":
                    the_modify = self.req_pairs[req_id]["request"]["params"]
                    rsp_time = self.req_pairs[req_id]["rsp_time"]
                    the_modify["rsp_time"] = rsp_time
                    modify_information.append(the_modify)
            if len(modify_information) > 1:
                print("\n母单存在修改")
                df = pd.DataFrame(modify_information, columns=["rsp_time", "action", "start_monitor_time", "end_monitor_time", "note"])
                with pd.option_context("display.max_colwidth", 100, "display.width", 200):
                    display(df)
            # 母单关联的股票信息
            df_gradecondition_detail = pd.DataFrame(self.gradecondition_info[order_no]["instruction_params"], columns=self.columns["gradecondition_create_detail"])
            gradecondition_stocks = list(set(df_gradecondition_detail["symbol"].tolist()))
            print("\n母单关联的股票", len(gradecondition_stocks), gradecondition_stocks)
            condition_list = set(df_gradecondition_detail["condition"].to_list())
            print("\n监控条件列表", condition_list)
            print("\n母单股票委托表")
            display(df_gradecondition_detail)
            # 母单推送详情
            if order_no not in self.gradecondition_push.keys():
                print("\n当前母单无推送信息", order_no)
            else:
                pushdata = self.gradecondition_push[order_no]["grade_instruction"]
                print('\n母单首条推送', json.dumps(pushdata[0]))
                df_gradecondition_push_instruction = pd.DataFrame(pushdata, columns=self.columns["gradecondition_push_instruction"])
                print('\n母单推送列表')
                display(df_gradecondition_push_instruction)
            
        
    def show_condition_order_detail(self, order_no):
        if order_no not in self.gradecondition_push.keys():
            print("母单id: %s 没有子单推送" % order_no)
        else:
            push_condition = []
            grade_conditions  = self.gradecondition_push[order_no]["grade_condition"]
            for symbol, condition in grade_conditions.items():
                push_condition.append(condition[-1])
            df_grade_condition = pd.DataFrame(push_condition, columns=self.columns["gradecondition_push_condition"])
            condition_list = set(df_grade_condition["condition"].to_list())
            print("监控条件列表", condition_list)
            print("子单状态表")
            display(df_grade_condition)
    
    
    def show_condition_security_order_detail(self, order_no, fund, security):
        if order_no not in self.gradecondition_push.keys():
            print("母单id: %s 没有子单推送" % order_no)
        else:
            if security not in self.gradecondition_push[order_no]["grade_condition"].keys():
                print("母单下 %s 证券代码 %s 没有推送记录" % (order_no, security))
            else:
                print("子单个股下单参数", security)
                condition_params = next((item for item in self.gradecondition_info[order_no]["instruction_params"] if item["symbol"] == security), None)
                print(json.dumps(condition_params))
                print("\n子单个股推送结果", order_no, security)
                pushdata = self.gradecondition_push[order_no]["grade_order"][security]
                df = pd.DataFrame(pushdata, columns=self.columns["gradecondition_push_order"])
                msg_list = [item["Text"] for item in pushdata]
                print("错误信息列表", set(msg_list))
                display(df)
        
        
    def show_condition_initreqs(self, order_no, isfullreqs=False):
        req_id = ""
        if order_no in self.req_pairs.keys():
            req_id = order_no
        if order_no in self.gradecondition_info.keys():
            req_id = self.gradecondition_info[order_no]["req_id"]
        if req_id != "":
            self.show_request_and_response(req_id, isfullreqs)
        else:
            print("找不到id[%s]关联的原始请求信息" % order_no)


    # 综合处理
    # 查询组合条件单 json rpc.gradecondition query_gradecondition
    # 查询条件单 待处理
    def handle_condition_query(self):
        self.gradecondition_query_dict = {}
        self.query_gradecondition_df = {}
        # 条件单 query_condition
        
        # 组合条件单 查询母单 query_gradecondition
        self.gradecondition_query_dict = self._handle_query_result("json", "rpc.gradecondition", "query_gradecondition", "data")
        columns_gradecondition_querydata = ["rsp_time", "fund", "order_from", "order_no", "create_time", "update_time", "status_msg", "price_type", "side", "note"]
        for rsp_time, query_data in self.gradecondition_query_dict.items():
            df_query_gradecondition = ""
            if len(query_data) > 0:
                df_query_gradecondition = pd.DataFrame(query_data, columns=columns_gradecondition_querydata)
            query_index = rsp_time + "|gradecond|" + str(len(query_data))
            self.query_gradecondition_df[query_index] = df_query_gradecondition
        # 组合条件单 查询子单 query_condition 待处理
        # get_request_list("pb", "rpc.gradecondition", "query_condition")
        columns_gradecondition_querysuborder = [
            "rsp_time", "fund", "symbol", "side", "qty", "qty_order", "qty_trade","price", "price_type", "price_limit",
            "condition", "status_msg","create_time", "trigger_time", "trigger_tips"
        ]
        
        
    def show_querycondition(self, querytime):
        df_query_condition = self.query_gradecondition_df[querytime]
        if isinstance(df_query_condition, pd.DataFrame) and not df_query_condition.empty:
            display(df_query_condition)
        else:
            print("本次条件单查询结果为空")


    def p():
        pass

