# from flask import Flask
# from flask_cors import CORS
# from pymongo.mongo_client import MongoClient
# from dotenv import load_dotenv

# from config import Config
# import os


# def create_app(config_class = Config):
#     load_dotenv()
#     app = Flask(__name__)
#     app.config.from_object(config_class)
#     # CORS(app)

#     # Configure Database
#     cluster  = MongoClient(os.getenv('MONGODB_URI'))
#     try:
#         cluster .admin.command('ping')
#         print("Pinged your deployment. You successfully connected to MongoDB!")
#     except Exception as e:
#         print(e)
#     global db
#     db = cluster[os.getenv('MONGO_DB')]

#     # Register blueprint of application
#     # from app.main import bp as main_bp
#     # app.register_blueprint(main_bp)

#     # from app.projects import bp as project_bp
#     # app.register_blueprint(project_bp,url_prefix="/projects")

#     # from app.socialMedia import bp as socialMedia_bp
#     # app.register_blueprint(socialMedia_bp,url_prefix="/social-media")

#     @app.route('/test')
#     def test_page():
#         return f'Hello, World!'
    
#     return app

from fastapi import FastAPI
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
load_dotenv()
cluster  = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
try:
    cluster .admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
global db
db = cluster[os.getenv('MONGO_DB')]

from app.socialMedia import router as SocialMediaRouter
app.include_router(SocialMediaRouter, tags=["Social Media"],prefix="/social-media")

@app.get("/test",tags=["Root"])
async def read_root():
    return {"message": "Welcome!"}