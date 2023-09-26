from fastapi import FastAPI
import boto3
import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

def create_app():
    global app, db, s3
    app = FastAPI()
    load_dotenv()
    cluster=MongoClient(os.getenv('MONGODB_URI'))
    try:
        cluster .admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    db = cluster[os.getenv('MONGO_DB')]
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS"],
        aws_secret_access_key=os.environ['AWS_SECRET'],
        region_name=os.environ["AWS_REGION"]
    )

    from app.socialMedia.routes import router as SocialMediaRouter
    app.include_router(SocialMediaRouter, tags=["Social Media"],prefix="/social-media")

    @app.get("/test",tags=["Root"])
    async def read_root():
        return {"message": "Welcome!"}
    return app