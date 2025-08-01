from flask import jsonify
from functools import wraps
import pandas as pd
import numpy as np
import json
import traceback

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")  # 转为列表形式的字典
        elif isinstance(obj, pd.Series):
            return obj.tolist()  # Series转为列表
        elif isinstance(obj, np.integer):
            return int(obj)  # 处理numpy整数类型
        elif isinstance(obj, np.floating):
            if pd.isna(obj):
                return None  # 转换 NaN 为 null
            return float(obj)  # 处理numpy浮点数类型
        elif isinstance(obj, np.ndarray):
            return obj.tolist()  # numpy数组转为列表
        elif isinstance(obj, set):
            return list(obj)  # set转为列表
        return super().default(obj)

# 递归处理字典中的不可序列化类型
def convert_data(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                data[key] = value.to_dict(orient='records')  # 转换 DataFrame 为可序列化结构
            elif isinstance(value, set):
                data[key] = list(value)  # 转换 set 为 list
            elif isinstance(value, float) and pd.isna(value):
                data[key] = None  # 转换 NaN 为 null
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

            if (data != None):
                convert_data(data)

            print(f"服务器端 - data类型: {type(data)}")
            response = jsonify({
                'code': code,
                'data': data,
                'message': message
            })
            response.headers['Content-Type'] = 'application/json'
            print(f"服务器端 - 响应类型: {type(response)}")
            print(f"服务器端 - 响应头: {dict(response.headers)}")
            return response
        except Exception as e:
            # 输出详细的错误堆栈信息
            print(f"接口 {func.__name__} 发生错误: {e}")
            print("错误堆栈:")
            print(traceback.format_exc())

            response = jsonify({
                'code': -1,
                'data': None,
                'message': f'服务器内部错误: {str(e)}'
            })
            response.headers['Content-Type'] = 'application/json'
            return response
    return wrapper
