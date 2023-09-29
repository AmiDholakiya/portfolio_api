import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.collection import Collection
from bson import ObjectId

from app import db
from app.helper import validateToken, verify_password, create_access_token, create_refresh_token, get_token_data
from app.user.routes import user_col
from app.authentication.models import TokenSchema, Authentication

authentication_col:Collection = db.get_collection("authenticationTB")
router = APIRouter()

@router.post("/",response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    existing_token = authentication_col.find_one({"username":form_data.username})
    if existing_token is not None:
        isValid = await get_token_data(existing_token["access_token"])
        if isValid is not None:
            return {
                "access_token": existing_token["access_token"] ,
                "refresh_token": existing_token["refresh_token"]
            }
        else:
            authentication_col.delete_one({"_id":ObjectId(existing_token["_id"])}) 
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
    access_token = create_access_token({"email":user['email']})
    refresh_token = create_refresh_token({"email":user['email']})
    try:
        authentication = Authentication(**{"username":str(form_data.username),"client_id":str(form_data.client_id or ""),"access_token":access_token,"refresh_token":refresh_token,"created_at":datetime.datetime.now()})
        authentication_col.insert_one(authentication.__dict__)
        return {
            "access_token": access_token ,
            "refresh_token": refresh_token
        }
    except Exception as e:
        print("Error while Login ----> ",e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )                                
 
@router.post("/verify")
async def read_items(loginData = Depends(validateToken)):
    if loginData is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied! Please Login Again"
        )
    return {"token": loginData}