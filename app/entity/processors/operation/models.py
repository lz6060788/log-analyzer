from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogLine:
    """日志行"""
    content: str
    type: str = "operation"
    time: str = ""
    position: str = ""

class ProcessingState:
    """处理状态类"""

    def __init__(self):
        # 基础统计
        self.counts = 0

        # 日志列表
        self.log_list = []