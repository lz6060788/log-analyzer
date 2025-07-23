import json
from flask import Blueprint, request, jsonify, session
from entity.processors.clientprocessor import ClientProcessor
from utils.request import standard_json_response

"""
  客户端全量日志处理路由
"""
client_bp = Blueprint('log_client', __name__, url_prefix='/client')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'log'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@client_bp.route('/')
def profile():
    return "暂未实现"

@client_bp.route('/upload', methods=['POST'])
@standard_json_response
def upload_file():
    # 检查是否有文件部分
    if 'file' not in request.files:
        return None, -1, '文件不存在'
    
    file = request.files['file']

    # 如果用户没有选择文件
    if file.filename == '':
        return None, -1, '文件不存在'

    # 检查文件类型是否允许
    if not (file and allowed_file(file.filename)):
        return None, -1, '非日志文件，请勿上传'
    
    try:
        # 尝试以文本形式读取
        file_content = file.read().decode('gb2312', errors='ignore')  # 忽略无法解码的字符
        # print(file_content)
        clientreq = ClientProcessor([file_content])
        clientreq.parse()
        clientreq.handle_basket_order_push()
        clientreq.handle_algorithm_push()
        session['clientPropcessor'] = clientreq
        print("解析完成", "解析失败日志行数:", len(clientreq.illegal_reqs))
        print("跳过不处理的日志行数:", len(clientreq.skipped_reqs))
        return None
    except UnicodeDecodeError as e:
        return None, -1, '文件解析失败'

@client_bp.route('/query_fetch_statistics', methods=['GET'])
@standard_json_response
def query_fetch_statistics():
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.show_request_statics()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/query_accounts_logs', methods=['GET'])
@standard_json_response
def query_accounts_logs():
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.query_accounts_df
    else:
        return None, -1, '请先上传文件'
    
@client_bp.route('/query_fund_logs', methods=['GET'])
@standard_json_response
def query_funds_data():
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_fund_query_data()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/query_position_logs', methods=['GET'])
@standard_json_response
def query_position_data():
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_position_query_data()
    else:
        return None, -1, '请先上传文件'
    
@client_bp.route('/query_order_logs', methods=['GET'])
@standard_json_response
def query_order_data():
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_order_query_data()
    else:
        return None, -1, '请先上传文件'

