from flask import jsonify
from functools import wraps
import pandas as pd
import numpy as np
import json

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")  # 转为列表形式的字典
        elif isinstance(obj, pd.Series):
            return obj.tolist()  # Series转为列表
        elif isinstance(obj, np.integer):
            return int(obj)  # 处理numpy整数类型
        elif isinstance(obj, np.floating):
            return float(obj)  # 处理numpy浮点数类型
        elif isinstance(obj, np.ndarray):
            return obj.tolist()  # numpy数组转为列表
        return super().default(obj)
    
# 递归处理字典中的 DataFrame 类型
def convert_data(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                data[key] = value.to_dict(orient='records')  # 转换 DataFrame 为可序列化结构
            else:
                convert_data(value)  # 递归处理嵌套结构
    elif isinstance(data, list):
        for item in data:
            convert_data(item)  # 递归处理列表中的内容

def standard_json_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # 如果视图函数返回的是元组，第一个元素是data，第二个是code，第三个是message
            if isinstance(result, tuple):
                data, code, message = result
            else:
                data, code, message = result, 0, 'Success'

            convert_data(data)

            return jsonify({
                'code': code,
                'data': data,
                'message': message
            })
        except Exception as e:
            return jsonify({
                'code': 500,
                'data': None,
                'message': str(e)
            })
    return wrapper
