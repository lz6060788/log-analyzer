"""
统计处理器模块
负责请求统计、数据展示和汇总统计
"""

import json
from typing import Dict, List, Any
import pandas as pd

from .models import StatisticsResult, ProcessingState


class StatisticsProcessor:
    """统计处理器类"""
    
    def __init__(self, state: ProcessingState):
        self.state = state
    
    def parse_request_statistics(self) -> None:
        """
        解析请求统计数据
        """
        self.state.request_statics = {"pb": {}, "json": {}, "json_funid": {}}
        request_statics = self.state.request_statics
        
        for key, item in self.state.req_pairs.items():
            self.state.counts += 1
            request = item["request"]
            req_time = item["req_time"]
            req_type = item["protocol"]
            servicename = ""
            action = ""
            
            if req_type == "pb":
                self.state.counts_pb += 1
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
                self.state.counts_json += 1
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
                self.state.counts_funid += 1
                servicename = request["method"]
                action = str(request["params"]["FunID"])
            
            if servicename not in request_statics[req_type].keys():
                request_statics[req_type][servicename] = {}
            if action not in request_statics[req_type][servicename].keys():
                request_statics[req_type][servicename][action] = []
            
            request_statics[req_type][servicename][action].append({
                "key": key, 
                "lens": len(json.dumps(item)), 
                "req_time": req_time
            })
    
    def show_request_statics(self) -> List[StatisticsResult]:
        """
        展示请求统计数据
        
        Returns:
            统计结果列表
        """
        request_statics = self.state.request_statics
        
        cnt = 0
        sum_requests = []
        
        for k1, v1 in request_statics.items():
            for k2, v2 in request_statics[k1].items():
                for k3, v3 in request_statics[k1][k2].items():
                    total_lens = sum(d["lens"] for d in v3)
                    avg_lens = total_lens / len(v3) if len(v3) > 0 else 0
                    
                    sum_requests.append({
                        "protocol": k1, 
                        "servicename": k2, 
                        "action": k3, 
                        "counts": len(v3), 
                        "avg_lens": self._format_size(avg_lens), 
                        "total_lens": self._format_size(total_lens)
                    })
                    cnt += len(v3)
        
        print("总请求数：%d. pb请求数：%d, json请求数：%d, funid请求数：%d. 统计请求数：%d, 统计结果:【%s】" % (
            self.state.counts, self.state.counts_pb, self.state.counts_json, 
            self.state.counts_funid, cnt, cnt == (self.state.counts_pb + self.state.counts_json + self.state.counts_funid)
        ))
        
        return sum_requests
    
    def _format_size(self, size: float) -> str:
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
            size /= 1024.0
        return f"{size:.1f}P"
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        获取统计汇总信息
        
        Returns:
            统计汇总字典
        """
        return {
            "total_requests": self.state.counts,
            "pb_requests": self.state.counts_pb,
            "json_requests": self.state.counts_json,
            "funid_requests": self.state.counts_funid,
            "illegal_requests": len(self.state.illegal_reqs),
            "timeout_requests": len(self.state.timeout_reqs),
            "skipped_requests": len(self.state.skipped_reqs),
            "new_transmit_requests": len(self.state.new_transmit_reqs),
            "response_without_reqid": len(self.state.response_without_reqid),
            "lines_without_reqid": len(self.state.lines_without_reqid),
            "log_begin_time": self.state.log_begin_time,
            "log_end_time": self.state.log_end_time,
            "username": self.state.username,
            "userid": self.state.userid
        }
    
    def show_processing_summary(self) -> None:
        """
        显示处理汇总信息
        """
        summary = self.get_statistics_summary()
        
        print("\n=== 日志处理汇总 ===")
        print(f"总请求数: {summary['total_requests']}")
        print(f"PB请求数: {summary['pb_requests']}")
        print(f"JSON请求数: {summary['json_requests']}")
        print(f"FunID请求数: {summary['funid_requests']}")
        print(f"异常请求数: {summary['illegal_requests']}")
        print(f"超时请求数: {summary['timeout_requests']}")
        print(f"跳过请求数: {summary['skipped_requests']}")
        print(f"新传输请求数: {summary['new_transmit_requests']}")
        print(f"无请求ID响应数: {summary['response_without_reqid']}")
        print(f"无请求ID行数: {summary['lines_without_reqid']}")
        print(f"日志开始时间: {summary['log_begin_time']}")
        print(f"日志结束时间: {summary['log_end_time']}")
        print(f"用户名: {summary['username']}")
        print(f"用户ID: {summary['userid']}")
        print("=" * 30)
    
    def export_statistics_to_dataframe(self) -> pd.DataFrame:
        """
        导出统计数据到DataFrame
        
        Returns:
            统计数据DataFrame
        """
        request_statics = self.state.request_statics
        data = []
        
        for protocol, services in request_statics.items():
            for servicename, actions in services.items():
                for action, requests in actions.items():
                    total_lens = sum(d["lens"] for d in requests)
                    avg_lens = total_lens / len(requests) if len(requests) > 0 else 0
                    
                    data.append({
                        "protocol": protocol,
                        "servicename": servicename,
                        "action": action,
                        "counts": len(requests),
                        "avg_lens": self._format_size(avg_lens),
                        "total_lens": self._format_size(total_lens)
                    })
        
        return pd.DataFrame(data) 
