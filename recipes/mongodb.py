from pymongo import MongoClient
import json
import numpy as np

# Connect to MongoDB
client = MongoClient("mongodb+srv://ratu:ratu123@cluster0.r5gnp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["recipe_database"]
collection = db["recipes"]

with open("US_recipes.json", "r", encoding="utf-8") as file:
    recipes = json.load(file)
    print("Loaded recipes:", recipes)  
    if isinstance(recipes, str):
        recipes = json.loads(recipes)
    if isinstance(recipes, dict):
        recipes = list(recipes.values())

processed_recipes = []
for recipe in recipes:
    processed_recipe = {
        "cuisine": recipe.get("cuisine", ""),
        "title": recipe.get("title", ""),
        "serves": recipe.get("serves", ""),
        "rating": float(recipe.get("rating") or 0.0),
        "prep_time": int(recipe.get("prep_time") or 0),
        "cook_time": int(recipe.get("cook_time") or 0),
        "total_time": int(recipe.get("total_time") or 0),
        "nutrients": recipe.get("nutrients", {}),
        "description": recipe.get("description", "")
    }
    for key, value in processed_recipe.items():
        if (isinstance(value, float) or isinstance(value, int)) and np.isnan(value):
            processed_recipe[key] = None
    processed_recipes.append(processed_recipe)
    
print("Processed recipes:", processed_recipes) 

if processed_recipes:
    collection.insert_many(processed_recipes)
    print(f"Inserted {len(processed_recipes)} recipes into MongoDB.")
