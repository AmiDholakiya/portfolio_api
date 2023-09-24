from flask import Flask
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

from config import Config
import os


def create_app(config_class = Config):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

    # Configure Database
    cluster  = MongoClient(os.getenv('MONGODB_URI'))
    try:
        cluster .admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    global db
    db = cluster[os.getenv('MONGO_DB')]

    # Register blueprint of application
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.projects import bp as project_bp
    app.register_blueprint(project_bp,url_prefix="/projects")

    @app.route('/test')
    def test_page():
        return f'Hello, World!'
    
    return app
