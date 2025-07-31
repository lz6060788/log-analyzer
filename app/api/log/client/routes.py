import json
from flask import Blueprint, request, jsonify, session
from entity.processors.client.client_processor_new import ClientProcessorNew
from utils.request import standard_json_response
import traceback

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
        print('开始解析')
        
        # 添加详细的错误处理
        try:
            clientreq = ClientProcessorNew([file_content], isJupyter=False)
            print('ClientProcessorNew 实例化成功')
        except Exception as e:
            print(f"ClientProcessorNew 实例化失败")
            print("错误堆栈:")
            print(traceback.format_exc())
            return None, -1, f'处理器初始化失败: {str(e)}'
        
        try:
            clientreq.parse()
            print('解析完成')
        except Exception as e:
            print(f"解析过程失败")
            print("错误堆栈:")
            print(traceback.format_exc())
            return None, -1, f'文件解析失败: {str(e)}'
        
        session['clientPropcessor'] = clientreq
        print("解析完成", "解析失败日志行数:", len(clientreq.state.illegal_reqs))
        print("跳过不处理的日志行数:", len(clientreq.state.skipped_reqs))
        return None
    except UnicodeDecodeError as e:
        print(f"文件解码失败")
        print("错误堆栈:")
        print(traceback.format_exc())
        return None, -1, '文件解析失败'
    except Exception as e:
        print(f"未知错误")
        print("错误堆栈:")
        print(traceback.format_exc())
        return None, -1, f'处理失败: {str(e)}'

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
        return clientreq.account_processor.query_accounts_df
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

@client_bp.route('/query_order_summary', methods=['GET'])
@standard_json_response
def query_order_summary():
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_order_summary()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/trade_query_data', methods=['GET'])
@standard_json_response
def get_trade_query_data():
    """获取成交查询数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_trade_query_data()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/query_trade_summary', methods=['GET'])
@standard_json_response
def query_trade_summary():
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_trade_summary()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/position_querytime/<fundkey>', methods=['GET'])
@standard_json_response
def get_position_querytime(fundkey):
    """获取持仓查询时间列表"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_position_querytime(fundkey)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/order_querytime/<fundkey>', methods=['GET'])
@standard_json_response
def get_order_querytime(fundkey):
    """获取委托查询时间列表"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_order_querytime(fundkey)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/trade_querytime/<fundkey>', methods=['GET'])
@standard_json_response
def get_trade_querytime(fundkey):
    """获取成交查询时间列表"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_trade_querytime(fundkey)
    else:
        return None, -1, '请先上传文件'

# 新股申购相关路由
@client_bp.route('/ipo_query_data', methods=['GET'])
@standard_json_response
def get_ipo_query_data():
    """获取新股申购额度查询数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        fund = request.args.get('fund')
        return clientreq.get_ipo_query_data(fund if fund else None)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/ipo_lottery_data', methods=['GET'])
@standard_json_response
def get_ipo_lottery_data():
    """获取新股中签明细查询数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        fund = request.args.get('fund')
        return clientreq.get_ipo_lottery_data(fund if fund else None)
    else:
        return None, -1, '请先上传文件'

# 篮子交易相关路由
@client_bp.route('/basket_summary_data', methods=['GET'])
@standard_json_response
def get_basket_summary_data():
    """获取篮子订单汇总数据"""
    source = request.args.get('source')
    fund = request.args.get('fund', '')
    stockcode = request.args.get('stockcode', '')
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_basket_summary_data(source, fund, stockcode)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/basket_instance_detail', methods=['GET'])
@standard_json_response
def get_basket_instance_detail():
    """获取指定母单的实例详情"""
    instanceid = request.args.get('instanceid')
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_basket_instance_detail(instanceid)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/basket_order_detail', methods=['GET'])
@standard_json_response
def get_basket_order_detail():
    """获取指定母单的全部子单详情"""
    instanceid = request.args.get('instanceid')
    fund = request.args.get('fund', '')
    stockcode = request.args.get('stockcode', '')
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_basket_order_detail(instanceid, fund, stockcode)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/basket_query_data', methods=['GET'])
@standard_json_response
def get_basket_query_data():
    """获取篮子订单查询数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        querytime = request.args.get('querytime')
        return clientreq.get_basket_query_data(querytime)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/basket_initreqs', methods=['GET'])
@standard_json_response
def get_basket_initreqs():
    """获取指定母单的原始请求明细"""
    instance = request.args.get('instance')
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_basket_initreqs(instance)
    else:
        return None, -1, '请先上传文件'


# 算法交易相关路由
@client_bp.route('/get_new_algorithm_order', methods=['GET'])
@standard_json_response
def get_new_algorithm_order():
    """获取当日新增的算法订单"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_new_algorithm_order()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/algorithm_code', methods=['GET'])
@standard_json_response
def get_algorithm_code():
    """获取算法订单涉及的股票代码列表"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_algorithm_code()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/algorithm_detail', methods=['GET'])
@standard_json_response
def get_algorithm_detail():
    """获取指定算法订单的明细"""
    instanceid = request.args.get('instanceid')
    clientreq = session.get('clientPropcessor')
    if clientreq:
        result = clientreq.get_algorithm_detail(instanceid)
        return result.to_dict('records') if result is not None else None
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/algorithm_push_detail', methods=['GET'])
@standard_json_response
def get_algorithm_push_detail():
    """获取算法订单推送明细"""
    instanceid = request.args.get('instanceid')
    push_type = request.args.get('push_type')
    clientreq = session.get('clientPropcessor')
    if clientreq:
        push_type = request.args.get('push_type', '')
        return clientreq.get_algorithm_push_detail(instanceid, push_type)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/algorithm_query_data', methods=['GET'])
@standard_json_response
def get_algorithm_query_data():
    """获取算法订单查询数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_algorithm_query_data()
    else:
        return None, -1, '请先上传文件'

# 条件交易相关路由
@client_bp.route('/condition_summary_data', methods=['GET'])
@standard_json_response
def get_condition_summary_data():
    """获取条件单汇总数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_condition_summary_data()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/condition_instance_detail_data/<order_no>', methods=['GET'])
@standard_json_response
def get_condition_instance_detail_data(order_no):
    """获取条件单实例明细数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_condition_instance_detail_data(order_no)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/condition_order_detail_data/<order_no>', methods=['GET'])
@standard_json_response
def get_condition_order_detail_data(order_no):
    """获取条件单母单操作明细数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_condition_order_detail_data(order_no)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/condition_security_order_detail_data/<order_no>', methods=['GET'])
@standard_json_response
def get_condition_security_order_detail_data(order_no):
    """获取条件单证券操作明细数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        fund = request.args.get('fund', '')
        security = request.args.get('security', '')
        return clientreq.get_condition_security_order_detail_data(order_no, fund, security)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/condition_initreqs_data/<order_no>', methods=['GET'])
@standard_json_response
def get_condition_initreqs_data(order_no):
    """获取条件单初始请求数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_condition_initreqs_data(order_no)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/querycondition_data/<querytime>', methods=['GET'])
@standard_json_response
def get_querycondition_data(querytime):
    """获取条件单查询数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_querycondition_data(querytime)
    else:
        return None, -1, '请先上传文件'

# 融资融券相关路由
@client_bp.route('/finable_security_data', methods=['GET'])
@standard_json_response
def get_finable_security_data():
    """获取可融资标的券数据"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        fund_key = request.args.get('fund_key')
        return clientreq.get_finable_security_data(fund_key if fund_key else None)
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/finable_security_failed', methods=['GET'])
@standard_json_response
def get_finable_security_failed():
    """获取可融资标的券失败查询"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_finable_security_failed()
    else:
        return None, -1, '请先上传文件'

@client_bp.route('/finable_security_querytime/<fundkey>', methods=['GET'])
@standard_json_response
def get_finable_security_querytime(fundkey):
    """获取指定资金账户的可融资标的券查询时间列表"""
    clientreq = session.get('clientPropcessor')
    if clientreq:
        return clientreq.get_finable_security_querytime(fundkey)
    else:
        return None, -1, '请先上传文件'

