from fastapi import APIRouter, UploadFile, File, Depends, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from pymongo.collection import Collection
import json
from bson import ObjectId

from app import db
from app.education.models import EducationCreateModel,EducationUpdateModel
from app.helper import get_S3_signed_URL, file_upload_s3, get_filename, delete_file_s3, validateToken
from . import MODEL_NAME

education_col:Collection = db.get_collection("educationTB")
router = APIRouter()

@router.get("/")
async def index(pageSize: int = 10, pageNumebr: int = 1, login_data = Depends(validateToken)):
    try:
        skips = pageSize * (pageNumebr - 1)
        resultList = list()
        total_document = education_col.count_documents({"user_id":login_data["_id"]})
        get_all = education_col.find({"user_id":login_data["_id"]},{"user_id":0,"created_at":0}).skip(skips).limit(pageSize).sort("created_at",1)
        for item in get_all:
            resultList.append(json.loads(json.dumps(item,default=str)))
        return {"data":resultList,"total":total_document,"count":len(resultList)}
    except Exception as e:
        print("Error While fetching Social Media----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/{id}")
async def get_education_ById(id:str,login_data = Depends(validateToken)):
    try:
        result = education_col.find_one({"_id": ObjectId(id),"user_id":login_data["_id"]},{"user_id":0,"created_at":0})
        if result is not None:
            return json.loads(json.dumps(result,default=str))
        return HTTPException(status_code=404, detail="Social Media is not exist")
    except Exception as e:
        print("Error While fetching Social Media----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/",response_description="Add new Social Media")
async def create_socialmedia(item: EducationCreateModel = Depends(), login_data = Depends(validateToken)):
    try:
        item.user_id = login_data["_id"]
        education = jsonable_encoder(item)
        education_col.insert_one(education)
        resultObj = json.loads(json.dumps(education,default=str))
        return JSONResponse(status_code=status.HTTP_200_OK,content=resultObj)
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.put("/{id}")
async def update_education(id:str, item:EducationUpdateModel = Depends(), login_data = Depends(validateToken) ):
    try :
        old_object = education_col.find_one({"_id": ObjectId(id), "user_id":login_data["_id"]})
        if old_object is None:
            return HTTPException(status_code=404, detail="Social Media is not exist")

        education = {k: v for k, v in item.model_dump().items() if v is not None and str(v) != ''}
        if len(education) >= 1:
            update_result = education_col.update_one({"_id": ObjectId(id),"user_id":login_data["_id"]}, {"$set": education})
            if update_result.modified_count == 1:
                print(update_result)
                return {"message": "Social Media Updated Successfully"}
        return {"message": "Social Media Updated Successfully"}
        
    except Exception as e:
        print("Error While updating SocialMedia ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/{id}")
async def delete_education(id:str, login_data = Depends(validateToken)):
    try:
        delete_result = education_col.find_one_and_delete({"_id": ObjectId(id), "user_id":login_data["_id"]})

        if delete_result is not None:
            return {"message":"Social Media Deleted"}

        return HTTPException(status_code=404, detail="Social Media is not exist")
    except Exception as e:
        print("Error while deleting SocialMedia ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")