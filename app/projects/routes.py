from fastapi import APIRouter, UploadFile, File, Depends, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo.collection import Collection
import json
from bson import ObjectId

from app import db
from app.projects.models import ProjectsCreateModel,ProjectsUpdateModel
from app.helper import get_S3_signed_URL, file_upload_s3, get_filename, delete_file_s3, validateToken
from . import MODEL_NAME

project_col:Collection = db.get_collection("projectTB")
router = APIRouter()

@router.get("/")
async def index(pageSize: int = 10, pageNumebr: int = 1, login_data = Depends(validateToken)):
    try:
        skips = pageSize * (pageNumebr - 1)
        resultList = list()
        total_document = project_col.count_documents({"user_id":login_data["_id"]})
        get_all = project_col.find({"user_id":login_data["_id"]},{"user_id":0,"created_at":0}).skip(skips).limit(pageSize).sort("created_at",1)
        for item in get_all:
            if "cover_file" in item:
                item['cover_file'] = get_S3_signed_URL(item['cover_file'])
            resultList.append(json.loads(json.dumps(item,default=str)))
        return {"data":resultList,"total":total_document,"count":len(resultList)}
    except Exception as e:
        print("Error While fetching Social Media----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/{id}")
async def get_project_ById(id:str,login_data = Depends(validateToken)):
    try:
        result = project_col.find_one({"_id": ObjectId(id),"user_id":login_data["_id"]},{"user_id":0,"created_at":0})
        if result is not None:
            if "cover_file" in result:
                result['cover_file'] = get_S3_signed_URL(result['cover_file']) 
            return json.loads(json.dumps(result,default=str))
        return HTTPException(status_code=404, detail="Social Media is not exist")
    except Exception as e:
        print("Error While fetching Social Media----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/",response_description="Add new Social Media")
async def create_project(item: ProjectsCreateModel = Depends(), file: UploadFile = File(...), login_data = Depends(validateToken)):
    try:
        unique_filename = get_filename(MODEL_NAME + "/" + login_data["email"],"cover_file",file.filename)
        file_upload_s3(file.file, unique_filename)
        item.cover_file = unique_filename
        item.user_id = login_data["_id"]
        if item.technologies is not None: item.technologies = json.loads(item.technologies)
        if item.tools is not None: item.tools = json.loads(item.tools)

        projectData = jsonable_encoder(item)
        project_col.insert_one(projectData)
        resultObj = json.loads(json.dumps(projectData,default=str))
        resultObj["cover_file"] = get_S3_signed_URL(resultObj["cover_file"])
        return JSONResponse(status_code=status.HTTP_200_OK,content=resultObj)
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.put("/{id}")
async def update_project(id:str, item:ProjectsUpdateModel = Depends(), file: UploadFile = File(None) ,login_data = Depends(validateToken) ):
    try :
        old_object = project_col.find_one({"_id": ObjectId(id), "user_id":login_data["_id"]})
        if old_object is None:
            return HTTPException(status_code=404, detail="Social Media is not exist")
        if file is not None:
            delete_file_s3(old_object["cover_file"])
            unique_filename = get_filename(MODEL_NAME + "/" + login_data["email"],"cover_file",file.filename)
            file_upload_s3(file.file, unique_filename)
            item.cover_file = unique_filename
        
        if item.technologies is not None:
            item.technologies = json.loads(item.technologies)
        if item.tools is not None:
            item.tools = json.loads(item.tools)
        project = {k: v for k, v in item.model_dump().items() if v is not None and str(v) != ''}
        if len(project) >= 1:
            update_result = project_col.update_one({"_id": ObjectId(id),"user_id":login_data["_id"]}, {"$set": project})
            if update_result.modified_count == 1:
                return {"message": "Social Media Updated Successfully"}
        return {"message": "Social Media Updated Successfully"}
        
    except Exception as e:
        print("Error While updating SocialMedia ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/{id}")
async def delete_project(id:str, login_data = Depends(validateToken)):
    try:
        delete_result = project_col.find_one_and_delete({"_id": ObjectId(id), "user_id":login_data["_id"]})

        if delete_result is not None:
            delete_file_s3(delete_result["cover_file"])
            return {"message":"Social Media Deleted"}

        return HTTPException(status_code=404, detail="Social Media is not exist")
    except Exception as e:
        print("Error while deleting SocialMedia ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")