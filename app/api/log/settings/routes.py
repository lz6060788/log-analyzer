from flask import Blueprint

setting_bp = Blueprint('setting', __name__, url_prefix='/setting')

@setting_bp.route('/')
def profile():
    return "User profile page"

@setting_bp.route('/edit')
def edit_profile():
    return "Edit profile page"
