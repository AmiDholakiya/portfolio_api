# from flask import Blueprint 

# bp = Blueprint("socialmedia",__name__)

# from app.socialMedia import routes

from fastapi import APIRouter, Body, encoders
from typing import List
from pymongo.collection import Collection

from app import db
from app.socialMedia.models import SocialMediaTB, SocialMedia_helper
from app.helper import PyObjectId

socialMedial_col:Collection = db.get_collection("socialMediaTB")
# socialMedial_col = db["socialMediaTB"]
router = APIRouter()

@router.get("/")
async def index():
    # result = socialMedial_col.find()
    # resultList:List(SocialMediaTB) = list()
    # for item in result:
    #     resultList.append(json.loads(json.dumps(item,default=str)))
    # return resultList
    resultList:List(SocialMediaTB) = list()

    async for student in socialMedial_col.find():
        resultList.append(SocialMedia_helper(student))
    return resultList

@router.post("/")
async def create(item: SocialMediaTB = Body()):
    # try:
    #     body = SocialMediaTB(**request.form.to_dict(flat=True))
    #     result = socialMedial_col.insert_one(item.__dict__)
    #     return {result:"Inserted Successfull"}
    #     # item.id = PyObjectId(str(result.inserted_id))
    #     # return item.to_json()
    # except Exception as e:
    #     print(e)
    #     return "Internal Server Error", 500
    try:
        socialMedia = encoders.jsonable_encoder(item)
        result = await socialMedial_col.insert_one(socialMedia)
        socialMedia["id"] = result.inserted_id
        return SocialMedia_helper(socialMedia)
    except Exception as error:
        print(error)
        return "Internal Server Error", 500