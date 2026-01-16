
from flask import Flask
from flask_cors import CORS
from .config import config_by_name

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize Extensions
    CORS(app)
    
    # Register Blueprints
    from .routes.api import api_bp
    from .routes.main import main_bp
    from .routes.analytics import analytics_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(analytics_bp) # analytics routes start with /dashboard and /api/analytics
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
