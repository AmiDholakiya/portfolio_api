from bson import ObjectId
from app import s3
import os
    
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

def get_S3_signed_URL(object_key:str, expiry=3600):
    return s3.generate_presigned_url('get_object', Params={'Bucket': os.environ["S3_BUCKET"],'Key':object_key},ExpiresIn=expiry)
                        