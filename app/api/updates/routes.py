from flask import Blueprint, jsonify, request, send_file, current_app
import os
import json
from datetime import datetime

updates_bp = Blueprint('updates', __name__, url_prefix='/updates')

@updates_bp.route('/flask/version', methods=['GET'])
def get_flask_version():
    """获取Flask应用版本信息"""
    try:
        # 使用基于Flask应用根目录的绝对路径
        app_root = current_app.root_path
        version_file = os.path.join(app_root, '..', 'static', 'updates', 'flask-version.json')
        version_file = os.path.abspath(version_file)
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version_info = json.load(f)
            return jsonify(version_info)
        else:
            return jsonify({'error': f'Version file not found at: {version_file}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@updates_bp.route('/flask/download', methods=['GET'])
def download_flask_app():
    """下载Flask应用"""
    try:
        # 使用基于Flask应用根目录的绝对路径
        app_root = current_app.root_path
        exe_file = os.path.join(app_root, '..', 'static', 'updates', 'flask_app.exe')
        exe_file = os.path.abspath(exe_file)
        
        if os.path.exists(exe_file):
            return send_file(
                exe_file,
                as_attachment=True,
                download_name='flask_app.exe',
                mimetype='application/octet-stream'
            )
        else:
            return jsonify({'error': f'Flask app not found at: {exe_file}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

