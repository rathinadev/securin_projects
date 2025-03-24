from fastapi import FastAPI, Query, Request
from typing import Optional
from pymongo import MongoClient
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
app = FastAPI()

client = MongoClient("mongodb+srv://ratu:ratu123@cluster0.r5gnp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["recipe_database"]
collection = db["recipes"]

# Mount the "static" directory (optional for CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 Templates
templates = Jinja2Templates(directory="templates")
@app.get("/api/recipes")
async def get_all_recipes(page: int = 1, limit: int = 10):
    """
    Returns a paginated list of all recipes,
    sorted by rating in descending order.
    """
    total_recipes = collection.count_documents({})
    
    recipes_cursor = (
        collection.find({}, {"_id": 0})
        .sort("rating", -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    
    recipes_list = list(recipes_cursor)

    return {
        "page": page,
        "limit": limit,
        "total": total_recipes,
        "data": recipes_list
    }
@app.get("/api/recipes/search")
async def search_recipes(
    title: Optional[str] = None,
    cuisine: Optional[str] = None,
    calories: Optional[str] = None,  
    total_time: Optional[str] = None, 
    rating: Optional[str] = None, 
    limit: int = Query(50, ge=1, le=100)
):
    query = {}

    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    
    if cuisine:
        query["cuisine"] = {"$regex": cuisine, "$options": "i"}

    def add_filter(value: str, field: str):
        conditions = {}
        try:
            value = value.strip()
            if ">=" in value:
                conditions["$gte"] = float(value.replace(">=", "").strip())
            elif "<=" in value:
                conditions["$lte"] = float(value.replace("<=", "").strip())
            elif ">" in value:
                conditions["$gt"] = float(value.replace(">", "").strip())
            elif "<" in value:
                conditions["$lt"] = float(value.replace("<", "").strip())
            else:
                conditions["$eq"] = float(value)
            
            return {field: conditions}
        except ValueError:
            return {} 

    if calories:
        query.update(add_filter(calories, "nutrients.calories"))

    if total_time:
        query.update(add_filter(total_time, "total_time"))

    if rating:
        query.update(add_filter(rating, "rating"))

    recipes_cursor = collection.find(query, {"_id": 0}).limit(limit)
    recipes_list = list(recipes_cursor)
    total_results = collection.count_documents(query)
    
    return {
        "total_results": total_results,
        "data": recipes_list
    }


@app.get("/")
async def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
