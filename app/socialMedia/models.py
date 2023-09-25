from pydantic import BaseModel, Field
from typing import Optional
from fastapi.encoders import jsonable_encoder

from app.helper import PyObjectId

class SocialMediaTB(BaseModel):
    # id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str

    def to_json(self):
        return jsonable_encoder(self,exclude_none=True)
        
    def to_bson(self):
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data["_id"] is None:
            data.pop("_id")
        return data
    
def SocialMedia_helper(socialMedia) -> dict:
    return {
        "id": str(socialMedia["_id"]),
        "name": str(socialMedia["name"])
    }