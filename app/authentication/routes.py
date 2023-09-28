from fastapi import APIRouter, UploadFile, File, Depends, Body, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from pymongo.collection import Collection
import json
from bson import ObjectId

from app import db
from app.helper import verify_password, create_access_token, create_refresh_token, get_token_data
from app.user.routes import user_col
from app.authentication.models import TokenSchema, Authentication

authentication_col:Collection = db.get_collection("authenticationTB")
router = APIRouter()

@router.post("/",response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # existing_token = authentication_col.find_one({"username":form_data.username})
    # if existing_token is not None:
    #     isValid = await get_token_data(existing_token["access_token"])
    #     if isValid:
    #         return {
    #             "access_token": "access_token" ,
    #             "refresh_token": "refresh_token"
    #         } 
    user = user_col.find_one({"email":form_data.username},{"created_at":0})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user['hashedPassword']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(user['email'])
    refresh_token = create_refresh_token(user['email'])
    authentication = Authentication(**{"username":str(form_data.username),"client_id":str(form_data.client_id or ""),"access_token":access_token,"refresh_token":refresh_token})
    authentication_col.insert_one(authentication.__dict__)
    return {
        "access_token": access_token ,
        "refresh_token": refresh_token
    }
    