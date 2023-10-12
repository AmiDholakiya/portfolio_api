from fastapi import APIRouter, UploadFile, File,Body,  Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo.collection import Collection
import json
from bson import ObjectId


from app import db
from app.user.models import UserCreateModel, UserUpdateModel
from app.helper import get_S3_signed_URL, file_upload_s3, get_filename, delete_file_s3, get_hashed_password, get_token_data, validateToken
from . import MODEL_NAME
from app.socialMedia.routes import socialMedia_col
from app.skill.routes import skill_col
from app.projects.routes import project_col

user_col:Collection = db.get_collection("userTB")
router = APIRouter()

@router.get("/")
async def index(pageSize: int = 10, pageNumebr: int = 1,loginData = Depends(validateToken)):
    # try:
    skip = pageSize * (pageNumebr - 1)
    resultList = list()
    total_document = user_col.count_documents({})
    get_all = user_col.find({},{"hashedPassword":0,"created_at":0}).skip(skip).limit(pageSize).sort("created_at",1)
    for item in get_all:
        if "profile_file" in item:
            item['profile_file'] = get_S3_signed_URL(item['profile_file'])
        socialMediaList = list()
        for socialMedia in socialMedia_col.find({"user_id":str(item["_id"])},{"_id":0,"name":0,"created_at":0,"user_id":0}):
            socialMedia["logo_file"] = get_S3_signed_URL(socialMedia["logo_file"])
            socialMediaList.append(json.loads(json.dumps(socialMedia,default=str)))
        item["social_media_list"] = socialMediaList
        resultList.append(json.loads(json.dumps(item,default=str)))
    return {"data":resultList,"total":total_document,"count":len(resultList)}
    # except Exception as e:
    #     print("Error While fetching User----->",e)
    #     raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/{id}")
async def get_User_ById(id:str,loginData = Depends(validateToken)):
    try:
        result = user_col.find_one({"_id": ObjectId(id)},{"hashedPassword":0,"created_at":0})
        if result is not None:
            if "profile_file" in result:
                result['profile_file'] = get_S3_signed_URL(result['profile_file'])
            socialMediaList = list()
            for socialMedia in socialMedia_col.find({"user_id":str(result["_id"])},{"_id":0,"name":0,"created_at":0,"user_id":0}):
                socialMedia["logo_file"] = get_S3_signed_URL(socialMedia["logo_file"])
                socialMediaList.append(json.loads(json.dumps(socialMedia,default=str)))
            result["social_media_list"] = socialMediaList
            return json.loads(json.dumps(result,default=str))
        return HTTPException(status_code=404, detail="User is not exist")
    except Exception as e:
        print("Error While fetching User----->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
 
@router.post("/",response_description="Add new User")
async def create_user(item: UserCreateModel = Depends(), profile_file: UploadFile = File(...),loginData = Depends(validateToken) ):
    try:
        existing_user = user_col.find_one({"email":item.email})
        if existing_user is not None:
           return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content="Email Already Exsist !") 
    except Exception as e:
        print("Error While Existing User check ---> ",e)
    item.location = "";
    if item.title is not None: item.title = json.loads(item.title)
    if item.city is not None: item.location += item.city + ","
    if item.country is not None: item.location += item.country

    item.hashedPassword = get_hashed_password(item.password)
    del item.password
    try:
        if profile_file is not None:
            unique_filename = get_filename(MODEL_NAME,f'{item.email}',profile_file.filename)
            file_upload_s3(profile_file.file, unique_filename)
            item.profile_file = unique_filename
        user = {k: v for k, v in item.model_dump().items() if v is not None and str(v) != ''}
        # user = jsonable_encoder(item)
        user_col.insert_one(user)
        resultObj = json.loads(json.dumps(user,default=str))
        resultObj["profile_file"] = get_S3_signed_URL(resultObj["profile_file"])
        del resultObj["hashedPassword"]
        return JSONResponse(status_code=status.HTTP_200_OK,content=resultObj)
    except Exception as error:
        print("Error while creating User ---> ",error)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.put("/")
async def update_user(loginData = Depends(validateToken),item:UserUpdateModel = Depends(), profile_file: UploadFile = File(None) ):
    try :
        old_object = user_col.find_one({"email":loginData["email"]})
        if old_object is None:
            return HTTPException(status_code=404, detail="Access Denied! Please Login Again")
        if profile_file is not None:
            delete_file_s3(old_object["profile_file"])
            # unique_filename = get_filename(MODEL_NAME,f'{item.email if item.email is not None else old_object["email"]}',profile_file.filename)
            unique_filename = get_filename(MODEL_NAME,f'{item.email or old_object["email"]}',profile_file.filename)

            file_upload_s3(profile_file.file, unique_filename)
            item.profile_file = unique_filename
        item.location = ""
        if item.title is not None: item.title = json.loads(item.title)
        if item.city is not None: item.location += item.city + ","
        item.location += item.country or old_object["country"]
        user = {k: v for k, v in item.model_dump().items() if v is not None and str(v) != ''}
        if len(user) >= 1:
            update_result = user_col.update_one({"_id": ObjectId(old_object["_id"])}, {"$set": user})
            if update_result.modified_count == 1:
                print(update_result)
                return {"message": "User Updated Successfully"}
        return {"message": "User Updated Successfully"}
        
    except Exception as e:
        print("Error While updating user ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/")
async def delete_user(loginData = Depends(validateToken)):
    try:
        delete_result = user_col.find_one_and_delete({"email": loginData["email"]})

        if delete_result is not None:
            delete_file_s3(delete_result["profile_file"])
            return {"message":"User Deleted"}

        return HTTPException(status_code=404, detail="User is not exist")
    except Exception as e:
        print("Error while deleting user ---->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.get("/web/{email}")
async def get_user_data(email:str):
    try:
        result = user_col.find_one({"email": email},{"hashedPassword":0,"created_at":0})
        if result is not None:
            if "profile_file" in result:
                result['profile_file'] = get_S3_signed_URL(result['profile_file'])

            socialMediaList = list()
            for socialMedia in socialMedia_col.find({"user_id":str(result["_id"])},{"created_at":0,"user_id":0}):
                socialMedia["logo_file"] = get_S3_signed_URL(socialMedia["logo_file"])
                socialMediaList.append(json.loads(json.dumps(socialMedia,default=str)))
            result["social_media_list"] = socialMediaList

            skillList = list()
            for skill in skill_col.find({"user_id":str(result["_id"])},{"created_at":0,"user_id":0}):
                skill["logo_file"] = get_S3_signed_URL(skill["logo_file"])
                skillList.append(json.loads(json.dumps(skill,default=str)))
            result["skill_list"] = skillList

            projectList = list()
            for project in project_col.find({"user_id":str(result["_id"])},{"created_at":0,"user_id":0}):
                project["cover_file"] = get_S3_signed_URL(project["cover_file"])
                projectList.append(json.loads(json.dumps(project,default=str)))
            result["project_list"] = projectList

            return json.loads(json.dumps(result,default=str))
        return HTTPException(status_code=404, detail="User is not exist")
    except Exception as e:
        print(f"Error while fetching front data {email}--->",e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
        