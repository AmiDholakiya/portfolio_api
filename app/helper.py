from fastapi import HTTPException
from bson import ObjectId
from app import s3
import os
import datetime

    
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
    return f"{model_name}/{folder_name}/" +str(datetime.datetime.now().timestamp()).replace(".","") + "_"+ file_name

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
    
                        