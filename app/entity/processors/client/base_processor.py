"""
基础处理器模块
负责日志解析、请求对匹配和基础工具方法
"""

import json
import traceback
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import (
    RequestPair, ProcessingConfig, ProcessingState, 
    RequestPairsDict, FundTokenMapping, FundMapping,
    LogLine
)


class BaseProcessor:
    """基础处理器类"""
    
    def __init__(self, isJupyter: bool = True):
        self.config = ProcessingConfig()
        self.state = ProcessingState(isJupyter)
        self.req_pairs: RequestPairsDict = {}
        
    def format_size(self, size: float) -> str:
        """
        格式化文件大小
        
        Args:
            size: 字节大小
            
        Returns:
            格式化后的大小字符串
        """
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024.0:
                return f"{size:.1f}{unit}" if unit != 'B' else f"{int(size)}{unit}"
            size /= 102.0
        return f"{size:.1f}P"
    
    def _find_key_in_dict(self, d: Dict[str, Any], target_key: str) -> List[Any]:
        """
        在字典中递归查找指定键的值
        
        Args:
            d: 要搜索的字典
            target_key: 目标键名
            
        Returns:
            找到的值列表
        """
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
    
    def _is_algorithm_push(self, line: str, d: List[str]) -> bool:
        """
        判断是否为算法推送
        
        Args:
            line: 日志行
            d: 算法推送关键词列表
            
        Returns:
            是否为算法推送
        """
        for key in d:
            if key in line:
                return True
        return False
    
    def parse_line(self, line: str) -> str:
        """
        解析单行日志
        
        Args:
            line: 日志行内容
            
        Returns:
            处理结果
        """
        # 处理特殊日志行
        if "new_transmit_" in line:
            self.state.new_transmit_reqs.append(line)
            self.state.log_list.append(LogLine(content=line, req_type="request", isNewTransmit=True))
            return ""
        elif "|timeout|" in line:
            self.state.timeout_reqs.append(line)
            self.state.log_list.append(LogLine(content=line, req_type="request", isTimeout=True))
            return ""
        elif "|" not in line:
            self.state.skipped_reqs.append(line)
            self.state.log_list.append(LogLine(content=line, req_type="request", isSkip=True))
            return ""

        try:
            # 解析日志行基本信息
            parts = line.split('|')
            req_time = parts[1]
            req_type = parts[2]
            log_level = parts[3]
            req_id = parts[4]
            self.state.log_list.append(LogLine(content=line, req_type=req_type, req_id=req_id, time=req_time))
        except Exception as e:
            print(f"parse line error: {e}")
            return ""
        
        # 记录日志时间范围
        if self.state.log_begin_time == "":
            self.state.log_begin_time = req_time
        self.state.log_end_time = req_time
        
        # 处理有请求ID的日志行
        if req_id != "":
            self._process_request_response(line, req_id, req_type, req_time)
        # 查询账户，没有req_id，特殊处理
        else:
            self._process_special_lines(line, req_type, req_time)
    
    def _process_request_response(self, line: str, req_id: str, req_type: str, req_time: str) -> str:
        """
        处理请求响应对

        Args:
            line: 日志行
            req_id: 请求ID
            req_type: 请求类型
            req_time: 请求时间

        Returns:
            处理结果
        """
        if req_id not in self.req_pairs.keys():
            self.req_pairs[req_id] = {
                "request": "", "response": "", 
                "req_time": "", "rsp_time": "", "protocol": ""
            }

        try:
            # 解析请求/响应内容
            split_line = line.split(self.config.split_map[req_type])
            req_split = split_line[1] if (len(split_line) > 1 and len(split_line[1]) > 2) else '{}'
            req_split = req_split.replace("******", "}]}}}},")
            req_split = req_split.replace("\r\n", "")
            req_json = json.loads(req_split)

            self.req_pairs[req_id][req_type] = req_json
            self.req_pairs[req_id][self.config.req_time_map[req_type]] = req_time

            # 设置协议类型
            if req_type == "request":
                self._set_protocol_type(req_id, line)

            # 提取用户名
            if self.state.username == "":
                self._extract_username(req_split, req_json)

        except Exception as e:
            self.state.illegal_reqs.append({
                "line": line,
                "e": e,
                "traceback_exc": traceback.format_exc(),
            })
            return ""
        
        return ""
    
    def _set_protocol_type(self, req_id: str, line: str) -> None:
        """
        设置协议类型
        
        Args:
            req_id: 请求ID
            line: 日志行
        """
        if "servicename" in line:
            self.req_pairs[req_id]["protocol"] = "pb"
        elif "FunID" in line:
            self.req_pairs[req_id]["protocol"] = "json_funid"
        elif "action" in line:
            self.req_pairs[req_id]["protocol"] = "json"
    
    def _extract_username(self, req_split: str, req_json: Dict[str, Any]) -> None:
        """
        提取用户名
        
        Args:
            req_split: 请求字符串
            req_json: 请求JSON
        """
        if "useraccount" in req_split:
            username_list = self._find_key_in_dict(req_json, "useraccount")
            self.state.username = username_list
    
    def _process_special_lines(self, line: str, req_type: str, req_time: str) -> str:
        """
        处理特殊日志行
        
        Args:
            line: 日志行
            req_type: 请求类型
            req_time: 请求时间
            
        Returns:
            处理结果
        """
        if "query accout result" in line:
            try:
                req_split = line.split(self.config.split_map['request'])[1]
                # 适配一下logbody有多条的情况
                logbody = json.loads(req_split)["params"]["logbody"]
                user_account_str = ""
                for item in logbody:
                    if item["event"] == "query accout result!":
                        user_account_str = item["msg"].replace("InitAccountList:: result", "")[1:-1]
                    self.state.userid = item["userid"]
                self.state.query_accounts[req_time] = user_account_str
            except:
                pass
        
        # 集中交易、篮子交易推送，没有req_id，特殊处理
        # 这里解析用到了fundtoken_dict数据，得先保存，后续解析
        elif "basket_order_push" in line:
            request_str = line.split(self.config.split_map["response"])[1]
            self.state.basketorder_push_raw.append([req_time, request_str])
            self.state.basketorder_push_cnts += 1
        # 算法交易推送
        elif self._is_altorithm_push(line, self.config.possible_algorithm_pushkey):
            request_str = line.split(self.config.split_map["response"])[1]
            self.state.algorithm_push_raw.append([req_time, request_str])
        # 组合条件推送
        elif "grade_instruction" in line:
            request_str = line.split(self.config.split_map["response"])[1]
            self.state.gradecondition_push_instruction.append([req_time, request_str])
        elif "grade_condition" in line:
            request_str = line.split(self.config.split_map["response"])[1]
            self.state.gradecondition_push_condition.append([req_time, request_str])
        elif "grade_order" in line:
            request_str = line.split(self.config.split_map["response"])[1]
            self.state.gradecondition_push_order.append([req_time, request_str])
        else:
            if req_type == "response":
                request_str = line.split(self.config.split_map["response"])[1]
                self.state.response_without_reqid.append([req_time, request_str])
            else:
                self.state.lines_without_reqid.append(line)
                # break
    
    def _process_account_query(self, line: str, req_time: str) -> str:
        """
        处理账户查询
        
        Args:
            line: 日志行
            req_time: 请求时间
            
        Returns:
            处理结果
        """
        try:
            req_split = line.split(self.config.split_map['request'])[1]
            logbody = json.loads(req_split)["params"]["logbody"]
            user_account_str = ""
            for item in logbody:
                if item["event"] == "query accout result!":
                    user_account_str = item["msg"].replace("InitAccountList:: result", "")[1:-1]
                self.state.userid = item["userid"]
            # 这里需要存储到账户查询模块中
            return ""
        except:
            return ""
    
    def _process_basket_push(self, line: str, req_time: str) -> str:
        """
        处理篮子推送
        
        Args:
            line: 日志行
            req_time: 请求时间
            
        Returns:
            处理结果
        """
        request_str = line.split(self.config.split_map["response"])[1]
        # 这里需要存储到篮子推送模块中
        return ""
    
    def _process_algorithm_push(self, line: str, req_time: str) -> str:
        """
        处理算法推送
        
        Args:
            line: 日志行
            req_time: 请求时间
            
        Returns:
            处理结果
        """
        request_str = line.split(self.config.split_map["response"])[1]
        # 这里需要存储到算法推送模块中
        return ""
    
    def _process_condition_push(self, line: str, req_time: str, push_type: str) -> str:
        """
        处理条件推送
        
        Args:
            line: 日志行
            req_time: 请求时间
            push_type: 推送类型
            
        Returns:
            处理结果
        """
        request_str = line.split(self.config.split_map["response"])[1]
        # 这里需要存储到条件推送模块中
        return ""
    
    def parse(self, file_list: List[str]) -> None:
        """
        解析日志文件列表
        
        Args:
            file_list: 文件内容列表
            mode: 模式，jupyter或web
        """
        self.req_pairs = {}
        
        if self.state.isJupyter:
            for file in file_list:
                with open(file, "r", encoding="gb2312", errors="ignore") as f:
                    for line in f:
                        self.parse_line(line)
        else:
            for file_content in file_list:
                for line in file_content.split("\n"):
                    self.parse_line(line)
        
        # 清理空请求
        self._clean_empty_requests()
    
    def _clean_empty_requests(self) -> None:
        """
        清理空的请求对
        """
        self.state.removed_reqs = {
            key: value for key, value in self.req_pairs.items() 
            if (len(json.dumps(value["request"])) <= 2 or len(json.dumps(value["response"])) <= 2)
        }
        self.req_pairs = {
            key: value for key, value in self.req_pairs.items() 
            if (len(json.dumps(value["request"])) > 2 and len(json.dumps(value["response"])) > 2)
        }
    
    def get_fund_by_fund_token(self, fund_token: str) -> str:
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
    
    def get_request_list(self, protocol: str, servicename: str, cmd: str) -> List[str]:
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

    def show_request_and_response(self, req_id: str, isfullreqs: bool = True) -> None:
        """
        显示请求和响应
        
        Args:
            req_id: 请求ID
            isfullreqs: 是否显示完整请求
        """
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
    
    def get_request_and_response(self, req_id: str) -> Dict[str, Any]:
        """
        获取请求和响应
        """
        item = self.req_pairs[req_id]
        return item["request"], item["response"]

    def _is_altorithm_push(self, line: str, d: List[str]) -> bool:
        """
        判断是否为算法推送
        
        Args:
            line: 日志行
            d: 算法推送关键词列表
            
        Returns:
            是否为算法推送
        """
        for key in d:
            if key in line:
                return True
        return False

    def _handle_query_result(self, protocol: str, servicename: str, cmd: str, resultkey: str) -> Dict[str, Any]:
        """
        处理查询结果
        
        Args:
            protocol: 协议类型
            servicename: 服务名称
            cmd: 命令
            resultkey: 结果键
            
        Returns:
            查询结果
        """
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
