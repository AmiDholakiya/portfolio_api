from pydantic import BaseModel, Field
from typing import Optional
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import datetime
from app.helper import PyObjectId

class ProjectsDBModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId,alias="_id")
    title: str
    project_type_id: str
    cover_file: str
    project_link: str
    technologies: list[str]
    tools: list[str]
    description: str
    source_code_link: str
    tag: str
    user_id:str 
    created_at: str

class ProjectsCreateModel(BaseModel):
    # id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    project_type_id: str
    cover_file: str | None = None
    project_link: str | None = None
    technologies: str
    tools: str | None = None
    description: str
    source_code_link: str | None = None
    tag: str | None = None
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
                "title": "facebook",
                "cover_file":"textfile.txt"
            }
        }

class ProjectsUpdateModel(BaseModel):
    # id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: Optional[str] = Field(default="")
    project_type_id: Optional[str] = Field(default="")
    project_link: Optional[str] = Field(default="")
    technologies: Optional[str] = Field(default=None)
    tools: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default="")
    source_code_link: Optional[str] = Field(default="")
    tag: Optional[str] = Field(default="")
    cover_file: Optional[str] = Field(default="")
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
                "title": "facebook",
                "cover_file":"textfile.txt"
            }
        }