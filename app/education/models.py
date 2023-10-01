from pydantic import BaseModel, Field
from typing import Optional
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import datetime
from app.helper import PyObjectId

class EducationDBModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId,alias="_id")
    university: str
    education_level: str
    field_of_study: str
    degree: str
    user_id:str 
    created_at: str
class EducationCreateModel(BaseModel):
    # id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    university: str
    education_level: str 
    field_of_study: str 
    degree: str
    user_id: str | None = None
    created_at: datetime.datetime = datetime.datetime.now()
    def to_json(self):
        return jsonable_encoder(self,exclude_none=True)
        
    def to_bson(self):
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data["_id"] is None:
            data.pop("_id")
        return data
    class Config:
        population_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "university": "vnsgu",
                "education_level":"master"
            }
        }

class EducationUpdateModel(BaseModel):
    # id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    university: Optional[str] = Field(default="")
    field_of_study: Optional[str] = Field(default="")
    degree: Optional[str] = Field(default="")
    education_level: Optional[str] = Field(default="")
    def to_json(self):
        return jsonable_encoder(self,exclude_none=True)
        
    def to_bson(self):
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data["_id"] is None:
            data.pop("_id")
        return data
    class Config:
        population_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "university": "vnsgu",
                "education_level":"master"
            }
        }