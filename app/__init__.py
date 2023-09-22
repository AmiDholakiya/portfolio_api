from flask import Flask
from flask_cors import CORS

from config import Config
import os


NODE_DB = os.environ.get('NODE_DB')

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.projects import bp as project_bp
    app.register_blueprint(project_bp,url_prefix="/projects")

    @app.route('/test')
    def test_page():
        return f'Hello, World! {NODE_DB}'
    
    return app;
