# user schema and user model for mongodb
from datetime import datetime
from pymongo import MongoClient
from config.config import MONGODB_URI

uri = MONGODB_URI

def connect_to_db():
    return MongoClient(uri).adis_database

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
            "contact": {
                "bsonType": "string",
                "description": "Contact must be a string"
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