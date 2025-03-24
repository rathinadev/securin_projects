from pymongo import MongoClient
from dotenv import load_dotenv
import os


def delete_all_data_from_db():
    
    client = MongoClient("mongodb+srv://ratu:ratu123@cluster0.r5gnp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")


    
    db = client['recipe_database']
    
    collections = db.list_collection_names()
    
    for collection_name in collections:
        collection = db[collection_name]
        collection.delete_many({})
        print(f"All documents deleted from collection: {collection_name}")
    
    print("All data deleted from the database.")

if __name__ == "__main__":
    delete_all_data_from_db()