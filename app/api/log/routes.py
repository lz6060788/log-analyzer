from flask import Blueprint, render_template
from .client.routes import client_bp

log_bp = Blueprint('log', __name__, url_prefix='/log')


# 注册子蓝图
log_bp.register_blueprint(client_bp)

@log_bp.route('/')
def user_home():
    return render_template("index.html")
