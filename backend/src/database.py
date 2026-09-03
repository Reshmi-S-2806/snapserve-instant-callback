# import os
# from motor.motor_asyncio import AsyncIOMotorClient
# from dotenv import load_dotenv

# load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI")
# DB_NAME = os.getenv("DB_NAME")

# client = AsyncIOMotorClient(MONGO_URI)
# db = client[DB_NAME]
# leads_collection = db.get_collection("leads")

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)

# Automatically targets the database defined in the URI path ('lead_connect_db')
db = client.get_default_database() 
leads_collection = db.get_collection("leads")