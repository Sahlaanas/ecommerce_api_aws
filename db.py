from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGO_DB_SETTINGS("URI"))
db = client[setattr.MONGO_DB_SETTINGS["DB_NAME"]]

# db_collection = db["Ecommerce"]