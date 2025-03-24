from pymongo import MongoClient

def clear_mongodb():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['CPE_DATABASE']
        collection = db['CPE_COLLECTION']
        
        result = collection.delete_many({})
        
        print(f"Deleted {result.deleted_count} documents from the collection")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    clear_mongodb()