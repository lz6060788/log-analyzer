from flask import Flask, render_template, session
from flask_session import Session
from api.log.routes import log_bp
from utils.request import CustomJSONEncoder

app = Flask(__name__, template_folder='../templates', static_folder='../static')
# 配置Session
app.config['SESSION_TYPE'] = 'filesystem'  # 指定存储类型
app.config['SESSION_PERMANENT'] = False  # 如果设置为True，则关闭浏览器会话不会过期
app.config['SESSION_USE_SIGNER'] = False  # 是否对发送到客户端的session_id进行签名
app.config['SESSION_KEY_PREFIX'] = 'log:'  # 存储键的前缀

# 配置自定义JSON编码器
app.json_encoder = CustomJSONEncoder

Session(app)

# 路由配置
app.register_blueprint(log_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
