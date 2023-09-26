# from flask import Blueprint 

# bp = Blueprint("socialmedia",__name__)

# from app.socialMedia import routes

from fastapi import APIRouter, Body, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from pymongo.collection import Collection
import json
from urllib.parse import quote as urlencode
import os
import datetime
from bson import ObjectId

from app import db, s3
from app.socialMedia.models import SocialMediaModel, SocialMediaAddModel, SocialMediaUpdateModel, SocialMedia_helper
from app.helper import get_S3_signed_URL

socialMedial_col:Collection = db.get_collection("socialMediaTB")
# socialMedial_col = db["socialMediaTB"]
router = APIRouter()

@router.get("/")
async def index():
    try:
        resultList:List(SocialMediaModel) = list()
        for item in socialMedial_col.find():
            if "logo_file" in item:
                item['logo_file'] = get_S3_signed_URL(item['logo_file'])
            resultList.append(json.loads(json.dumps(item,default=str)))
        return resultList
    except Exception as e:
        print("Error While fetching Social Media----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/{id}")
async def get_socialMedia_ById(id:str):
    try:
        result = socialMedial_col.find_one({"_id": ObjectId(id)})
        if result is not None:
            if "logo_file" in result:
                result['logo_file'] = get_S3_signed_URL(result['logo_file']) 
            return json.loads(json.dumps(result,default=str))
        return HTTPException(status_code=404, detail="Social Media is not exist")
    except Exception as e:
        print("Error While fetching Social Media----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/",response_description="Add new Social Media")
async def create_socialmedia(item: SocialMediaAddModel = Depends(), file: UploadFile = File(...)):
    try:
        unique_filename = item.name + "_"+ str(datetime.datetime.now().timestamp()).replace(".","") + "_" + file.filename
        s3.upload_fileobj(file.file, os.environ["S3_BUCKET"], unique_filename )

        item.logo_file = unique_filename
        socialMedia = jsonable_encoder(item)
        socialMedial_col.insert_one(socialMedia)
        resultObj = json.loads(json.dumps(socialMedia,default=str))
        resultObj["logo_file"] = get_S3_signed_URL(resultObj["logo_file"])
        return JSONResponse(status_code=status.HTTP_200_OK,content=resultObj)
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.put("/{id}")
async def update_socialMedia(id:str, item:SocialMediaUpdateModel = Depends(), file: UploadFile = File(None) ):
    try :
        if file is not None:
            print("in file upload")
            unique_filename = (item.name or "") + "_"+ str(datetime.datetime.now().timestamp()).replace(".","") + "_" + file.filename
            s3.upload_fileobj(file.file,os.environ['S3_BUCKET'],unique_filename)
            item.logo_file = unique_filename

        socialMedia = {k: v for k, v in item.model_dump().items() if v is not None and str(v) != ''}
        if len(socialMedia) >= 1:
            update_result = socialMedial_col.update_one({"_id": ObjectId(id)}, {"$set": socialMedia})
            if update_result.modified_count == 1:
                print(update_result)
                return {"message": "Social Media Updated Successfully"}
        if (socialMedial_col.find_one({"_id": ObjectId(id)})) is not None:
            return {"message": "Social Media Updated Successfully"}
        return HTTPException(status_code=404, detail="Social Media is not exist")
    except Exception as e:
        print("Error While updating SocialMedia ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/{id}")
async def delete_socialMedia(id:str):
    try:
        delete_result = socialMedial_col.delete_one({"_id": ObjectId(id)})

        if delete_result.deleted_count == 1:
            return {"message":"Social Media Deleted"}

        return HTTPException(status_code=404, detail="Social Media is not exist")
    except Exception as e:
        print("Error while deleting SocialMedia ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

