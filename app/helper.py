from fastapi import HTTPException
from bson import ObjectId
from app import s3
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from typing import Union,Any

from app.authentication.models import TokenPayload

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

def get_filename(model_name:str,folder_name:str,file_name:str):
    return f"{model_name}/{folder_name}/" +str(datetime.now().timestamp()).replace(".","") + "_"+ file_name

def get_S3_signed_URL(object_key:str, expiry=3600):
    try:
        return s3.generate_presigned_url('get_object', Params={'Bucket': os.environ["S3_BUCKET"],'Key':object_key},ExpiresIn=expiry)
    except Exception as e:
        print(f"Error While getting S3 signed URL ----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

def file_upload_s3(file:bytes,filename):
    try:
        s3.upload_fileobj(file, os.environ["S3_BUCKET"], filename)
    except Exception as e:
        print(f"Error While uploading file in S3 Bucket ----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

def delete_file_s3(key):
    s3.delete_object(Bucket=os.environ["S3_BUCKET"],Key=key)

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def create_access_token(data: Union[str, Any], expires_in: int = None) -> str:
    if expires_in is not None:
        expires_in = datetime.utcnow() + expires_in
    else:
        expires_in = datetime.today() + timedelta(minutes=float(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]))
    
    to_encode = {"exp": expires_in, "data": str(data)}
    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_SECRET_KEY"], os.environ["ALGORITHM"])
    return encoded_jwt  

def create_refresh_token(data: Union[str, Any], expires_in: int = None) -> str:
    if expires_in is not None:
        expires_in = datetime.utcnow() + expires_in
    else:
        expires_in = datetime.today() + timedelta(days=float(os.environ["REFRESH_TOKEN_EXPIRE_MINUTES"]))
    
    to_encode = {"exp": expires_in, "data": str(data)}
    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_REFRESH_SECRET_KEY"], os.environ["ALGORITHM"])
    return encoded_jwt

async def get_token_data(token: str ):
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=[os.environ["ALGORITHM"]])
        token_data = TokenPayload(**payload)
        print(token_data)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code = 401,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.JWTError as e:
        print(e)
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # user: Union[dict[str, Any], None] = db.get(payload.sub, None)
    
    
    # if user is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Could not find user",
    #     )
    
    return True
    
                        