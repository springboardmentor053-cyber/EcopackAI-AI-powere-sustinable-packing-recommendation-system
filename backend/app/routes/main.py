
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    """Root endpoint serving the testing UI."""
    return render_template('index.html')
