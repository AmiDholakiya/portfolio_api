from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import boto3
import os
from jwt.api_jwt import PyJWT

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

def create_app():
    global app, db, s3, jwt_obj
    app = FastAPI(
        openapi_prefix="/prod"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
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
    jwt_obj = PyJWT()

    from app.authentication.routes import router as LoginRouter
    app.include_router(LoginRouter, tags=["Login"], prefix="/login")

    from app.user.routes import router as UserRouter
    app.include_router(UserRouter, tags=["User"], prefix="/user")

    from app.socialMedia.routes import router as SocialMediaRouter
    app.include_router(SocialMediaRouter, tags=["Social Media"],prefix="/social-media")

    from app.projects.routes import router as ProjectsRouter
    app.include_router(ProjectsRouter, tags=["Projects"],prefix="/project")

    from app.education.routes import router as EducationRouter
    app.include_router(EducationRouter, tags=["Education"], prefix="/education")

    from app.certificate.routes import router as CertificateRouter
    app.include_router(CertificateRouter, tags=["Certificate"], prefix="/certificate")

    from app.skill.routes import router as SkillRouter
    app.include_router(SkillRouter, tags=["Skill"], prefix="/skill")

    @app.get("/test",tags=["Root"])
    async def read_root():
        return {"message": "Welcome!"}
    return app