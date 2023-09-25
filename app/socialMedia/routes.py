# from flask import request
from typing import List
from pymongo.collection import Collection
import json

from app import db
# from app.socialMedia import bp
from app.socialMedia.models import SocialMediaTB
# from app.helper import PyObjectId

col:Collection = db["socialMediaTB"]

# @bp.route('/')
# def index():
#     result = col.find()
#     resultList:List(SocialMediaTB) = list()
#     for item in result:
#         resultList.append(json.loads(json.dumps(item,default=str)))
#     return resultList

# @bp.route('/',methods=["POST"])
# def insert():
#     try:
#         body = SocialMediaTB(**request.form.to_dict(flat=True))
#         result = col.insert_one(body.__dict__)
#         body.id = PyObjectId(str(result.inserted_id))
        
#         return body.to_json()
#     except Exception as e:
#         print(e)
#         return "Internal Server Error", 500
    
