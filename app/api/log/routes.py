from flask import Blueprint, render_template, session
from .client.routes import client_bp
from .operation.routes import operation_bp
from utils.request import standard_json_response

log_bp = Blueprint('log', __name__, url_prefix='/log')


# 注册子蓝图
log_bp.register_blueprint(client_bp)
log_bp.register_blueprint(operation_bp)

@log_bp.route('/')
def user_home():
    return render_template("index.html")

@log_bp.route('/status', methods=['GET'])
@standard_json_response
def status():
    return {
        "client_status": True if session.get('clientPropcessor') else False,
        "operation_status": True if session.get('operationProcessor') else False
    }
