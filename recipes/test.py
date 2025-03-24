from fastapi import FastAPI
from pymongo import MongoClient
import json
import uvicorn
import numpy as np



app = FastAPI()
client = MongoClient("mongodb+srv://ratu:ratu123@cluster0.r5gnp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["recipe_database"]
collection = db["recipes"]

print(list(collection.find({}, {"_id": 0})))