from pydantic import BaseModel, Field
from typing import Optional, List, Any
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import datetime
from app.helper import PyObjectId

from app.socialMedia.models import SocialMediaDBModel

class UserBaseModel(BaseModel):
    first_name: str | None = None 
    last_name: str | None = None
    email: str | None = None
    mobile: str | None = None
    headline: str | None = None
    technologies: list[str] | None = None
    title: str | None = None
    profile_file: str | None = None
    class Config:
        population_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "firtName": "Joan",
                "lastName":"Deol",
                "email":"example@gmail.com"
            }
        }

class UserCreateModel(BaseModel):
    first_name: str 
    last_name: str 
    email: str 
    mobile: str | None = None
    headline: str | None = None
    technologies: str| None = None
    title: str
    profile_file: str | None = None
    created_at: datetime.datetime = datetime.datetime.now()
    password: str = Field(..., min_length=5, max_length=24, description="user password")
    hashedPassword: str | None = None

class UserUpdateModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    mobile: str | None = None
    headline: str | None = None
    technologies: str| None = None
    title: str | None = None
    profile_file: str | None = None

class UserDBModel(UserBaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashedPassword: str

class UserChangePasswordMode(BaseModel):
    newPassword : str
    oldPassword: str