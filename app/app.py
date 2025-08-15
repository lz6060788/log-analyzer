import os
import sys

# 设置环境变量解决Windows控制台编码问题
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 强制设置控制台编码
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass

from flask import Flask, render_template, session, jsonify, send_from_directory, request
from flask_session import Session
from api.log.routes import log_bp
from utils.request import CustomJSONEncoder
import mimetypes
from api.updates.routes import updates_bp
from pathlib import Path
import json

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# 配置MIME类型映射
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/html', '.html')

# 自定义静态文件路由，确保正确的Content-Type
@app.route('/static/<path:filename>')
def custom_static(filename):
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    file_path = os.path.join(static_folder, filename)

    if not os.path.exists(file_path):
        return "File not found", 404

    # 获取文件的MIME类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # 根据文件扩展名设置默认MIME类型
        if filename.endswith('.js'):
            mime_type = 'application/javascript'
        elif filename.endswith('.css'):
            mime_type = 'text/css'
        elif filename.endswith('.html'):
            mime_type = 'text/html'
        else:
            mime_type = 'application/octet-stream'

    return send_from_directory(static_folder, filename, mimetype=mime_type)

# 根路由，服务index.html
@app.route('/')
def index():
    static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    print(static_folder)
    return send_from_directory(static_folder, 'index.html', mimetype='text/html')

# 配置Session
app.config['SESSION_TYPE'] = 'filesystem'  # 指定存储类型
app.config['SESSION_PERMANENT'] = False  # 如果设置为True，则关闭浏览器会话不会过期
app.config['SESSION_USE_SIGNER'] = False  # 是否对发送到客户端的session_id进行签名
app.config['SESSION_KEY_PREFIX'] = 'log:'  # 存储键的前缀

# 配置自定义JSON编码器
app.json_encoder = CustomJSONEncoder

Session(app)

# 健康检查路由
@app.route('/readiness')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'message': 'Log Analyzer is running'
    })

# 路由配置
app.register_blueprint(log_bp)
app.register_blueprint(updates_bp)  # 添加更新路由

if __name__ == '__main__':
    print("🚀 启动Log Analyzer...")
    print("🌐 启动Flask服务器...")
    app.run(debug=True, host='0.0.0.0', port=5000)
