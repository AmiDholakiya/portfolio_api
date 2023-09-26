from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from pymongo.collection import Collection
import json
from bson import ObjectId

from app import db
from app.socialMedia.models import SocialMediaCreateModel,SocialMediaUpdateModel
from app.helper import get_S3_signed_URL, file_upload_s3, get_filename, delete_file_s3
from . import MODEL_NAME

socialMedial_col:Collection = db.get_collection("socialMediaTB")
router = APIRouter()

@router.get("/")
async def index(pageSize: int = 10, pageNumebr: int = 1):
    try:
        skips = pageSize * (pageNumebr - 1)
        resultList = list()
        total_document = socialMedial_col.count_documents({})
        get_all = socialMedial_col.find().skip(skips).limit(pageSize).sort("created_at",1)
        for item in get_all:
            if "logo_file" in item:
                item['logo_file'] = get_S3_signed_URL(item['logo_file'])
            resultList.append(json.loads(json.dumps(item,default=str)))
        return {"data":resultList,"total":total_document,"count":len(resultList)}
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
async def create_socialmedia(item: SocialMediaCreateModel = Depends(), file: UploadFile = File(...)):
    try:
        unique_filename = get_filename(MODEL_NAME,"logo_file",file.filename)
        file_upload_s3(file.file, unique_filename)
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
        old_object = socialMedial_col.find_one({"_id": ObjectId(id)})
        if old_object is None:
            return HTTPException(status_code=404, detail="Social Media is not exist")
        if file is not None:
            delete_file_s3(old_object["logo_file"])
            unique_filename = get_filename(MODEL_NAME,"logo_file",file.filename)
            file_upload_s3(file.file, unique_filename)
            item.logo_file = unique_filename

        socialMedia = {k: v for k, v in item.model_dump().items() if v is not None and str(v) != ''}
        if len(socialMedia) >= 1:
            update_result = socialMedial_col.update_one({"_id": ObjectId(id)}, {"$set": socialMedia})
            if update_result.modified_count == 1:
                print(update_result)
                return {"message": "Social Media Updated Successfully"}
        return {"message": "Social Media Updated Successfully"}
        
    except Exception as e:
        print("Error While updating SocialMedia ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/{id}")
async def delete_socialMedia(id:str):
    try:
        delete_result = socialMedial_col.find_one_and_delete({"_id": ObjectId(id)})

        if delete_result is not None:
            delete_file_s3(delete_result["logo_file"])
            return {"message":"Social Media Deleted"}

        return HTTPException(status_code=404, detail="Social Media is not exist")
    except Exception as e:
        print("Error while deleting SocialMedia ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")