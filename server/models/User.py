from db.connect import connect_to_db
from datetime import datetime
from pymongo import MongoClient

UserValidator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "email"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "email": {
                "bsonType": "string",
                "pattern": "@",
                "unique": True,
                "description": "must be a string containing '@' and is required"
            },
            "password": {
                "bsonType": "string",
                "description": "must be a string"
            },
            "profile_pic": {
                "bsonType": "string",
                "description": "URL must be a string"
            },
            "created_at": {
                "bsonType": "date",
                "description": "Date must be a date",
                "default": datetime.now()
            },
            "updated_at": {
                "bsonType": "date",
                "description": "Date must be a date",
                "default": datetime.now()
            }
        }
    }
}


db = connect_to_db()
try:
    UserModel = db['users']
except:
    UserModel = db.create_collection("users", validator=UserValidator)


# UserModel.insert_one({
#     "name": "ASDFASDFA",
#     "email": "check@123.in",
#     # "password": "[PASSWORD]",
#     "profile_pic": "https://example.com/profile.jpg",
#     # "created_at": datetime.now(),
#     # "updated_at": datetime.now()
# })

#  | db.create_collection("users", validator=UserValidator)





