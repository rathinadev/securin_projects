from fastapi import FastAPI , Request
from pymongo import MongoClient
from typing import Optional
import uvicorn
from bson import ObjectId
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="templates")

client = MongoClient("mongodb://localhost:27017/")
db = client["CPE_DATABASE"]
collection = db["CPE_COLLECTION"]
app = FastAPI()

@app.get("/api/cpes")
def get_cpes(page: int = 1, limit: int = 10):
    data = list(collection.find({}).skip((page-1)*limit).limit(limit))
    for item in data:
        item['_id'] = str(item['_id'])
    return data


@app.get("/api/cpes/search")
def search_cpes(
    cpe_title: Optional[str] = None,
    cpe_22_uri: Optional[str] = None,
    cpe_23_uri: Optional[str] = None,
    deprecation_date: Optional[str] = None,  
):
    query = {}
    
    if cpe_title:
        query['cpe_title'] = {'$regex': cpe_title, '$options': 'i'}  
    if cpe_22_uri:
        query['cpe_22_uri'] = {'$regex': cpe_22_uri, '$options': 'i'}
    if cpe_23_uri:
        query['cpe_23_uri'] = {'$regex': cpe_23_uri, '$options': 'i'}
    
    if deprecation_date:
        try:
            date = datetime.strptime(deprecation_date, '%Y-%m-%d')
            
            query['$or'] = [
                {'cpe_22_deprecation_date': {'$ne': None, '$lt': date}},
                {'cpe_23_deprecation_date': {'$ne': None, '$lt': date}}
            ]
        except ValueError:
            return {"error": "Invalid date . Use YYYY-MM-DD format"}
    
    data = list(collection.find(query))

    for item in data:
        item['_id'] = str(item['_id'])
        
    return data

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)










@app.get("/")
def read_root():
    return {"message": "Hello World"}