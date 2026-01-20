
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    """Landing page endpoint."""
    return render_template('landing.html')

@main_bp.route('/recommendation', methods=['GET'])
def tool():
    """Main recommendation tool endpoint."""
    return render_template('index.html')
