from typing import Dict, List, Any, Optional

from .models import LogLine, ProcessingState

class OperationProcessor:
    """操作日志处理器主类"""

    def __init__(self, file_list: List[str]):
        """
        初始化处理器

        Args:
            file_list: 文件内容列表
        """
        # 初始化基础处理器
        self.state = ProcessingState()

        # 存储文件列表
        self.file_list = file_list

    def parse(self) -> None:
        for file_content in self.file_list:
                for line in file_content.split("\n"):
                    self.parse_line(line)

    def parse_line(self, line: str) -> None:
        """
        解析日志行
        日志行格式如下：
        20250415 09:03:21:058:965 20250415 09:03:21:058	算法管理-算法交易窗口	点击菜单：卖出F2
        """
        if line.strip() == "":
            return

        # 按空白符分割
        parts = line.split()
        if len(parts) < 4:
            return

        # 时间：前两个字段
        time = f"{parts[0]} {parts[1]}"

        # position：倒数第二个字段按"-"分割后的第一个字段
        second_last_field = parts[-2]
        position = second_last_field.split("-")[0] if "-" in second_last_field else second_last_field

        # 解析日志行
        log_line = LogLine(content=line, type="operation", time=time, position=position)
        self.state.log_list.append(log_line)

    def get_log_list(self) -> List[LogLine]:
        """
        获取日志列表
        """
        return self.state.log_list

    def filter_log_list(self, content: List[str]) -> List[LogLine]:
        """
        过滤日志列表
        """
        subStrList = content.split("~")
        return [log for log in self.state.log_list if any(subStr in log.content for subStr in subStrList)]
