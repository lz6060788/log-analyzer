from flask import Blueprint, request, session
from entity.processors.operation.operation_processor import OperationProcessor
from utils.request import standard_json_response
import traceback

"""
  客户端全量日志处理路由
"""
operation_bp = Blueprint('log_operation', __name__, url_prefix='/operation')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'log'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@operation_bp.route('/')
def profile():
    return "暂未实现"

@operation_bp.route('/upload', methods=['POST'])
@standard_json_response
def upload_file():
    # 检查是否有文件部分
    if 'files' not in request.files:
        return None, -1, '文件不存在'

    files = request.files.getlist('files')

    # 如果用户没有选择文件
    if not files or all(file.filename == '' for file in files):
        return None, -1, '文件不存在'

    # 检查所有文件类型是否允许
    for file in files:
        if file.filename and not allowed_file(file.filename):
            return None, -1, f'文件 {file.filename} 非日志文件，请勿上传'

    try:
        # 合并所有文件内容
        all_file_contents = []
        for file in files:
            if file.filename:  # 确保文件不为空
                try:
                    file_content = file.read().decode('gb2312', errors='ignore')  # 忽略无法解码的字符
                    all_file_contents.append(file_content)
                except UnicodeDecodeError as e:
                    print(f"文件 {file.filename} 解码失败")
                    print("错误堆栈:")
                    print(traceback.format_exc())
                    return None, -1, f'文件 {file.filename} 解析失败'

        print('开始解析')

        # 添加详细的错误处理
        try:
            operationProcessor = OperationProcessor(all_file_contents)
            print('OperationProcessor 实例化成功')
        except Exception as e:
            print(f"OperationProcessor 实例化失败")
            print("错误堆栈:")
            print(traceback.format_exc())
            return None, -1, f'处理器初始化失败: {str(e)}'

        try:
            operationProcessor.parse()
            print('解析完成')
        except Exception as e:
            print(f"解析过程失败")
            print("错误堆栈:")
            print(traceback.format_exc())
            return None, -1, f'文件解析失败: {str(e)}'

        session['operationProcessor'] = operationProcessor
        return None
    except Exception as e:
        print(f"未知错误")
        print("错误堆栈:")
        print(traceback.format_exc())
        return None, -1, f'处理失败: {str(e)}'

@operation_bp.route('/filter_log_list', methods=['GET'])
@standard_json_response
def filter_log_list():
    operationProcessor = session.get('operationProcessor')
    if operationProcessor:
        content = request.args.get('content', "")
        start_time = request.args.get('startTime', "")
        end_time = request.args.get('endTime', "")
        return operationProcessor.filter_log_list(content, start_time, end_time)
    else:
        return None, -1, '请先上传文件'
