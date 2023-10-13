from pydantic import BaseModel, Field
from typing import Optional
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import datetime
from app.helper import PyObjectId

class CertificateDBModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId,alias="_id")
    title: str
    icon_file: str
    link: str
    user_id:str 
    created_at: str
class CertificateCreateModel(BaseModel):
    # id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    icon_file: str | None = None
    link: str 
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
                "title": "vnsgu",
                "icon_file":"master"
            }
        }

class CertificateUpdateModel(BaseModel):
    title: Optional[str] = Field(default="")
    link: Optional[str] = Field(default="")
    icon_file: Optional[str] = Field(default="")
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
                "title": "vnsgu",
                "icon_file":"master"
            }
        }