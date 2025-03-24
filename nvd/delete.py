import motor.motor_asyncio
import asyncio

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "cve_db"
COLLECTION_NAME = "cves"

async def delete_all_data():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://ratu:ratu123@cluster0.r5gnp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client[DB_NAME]
    cve_collection = db[COLLECTION_NAME]

    result = await cve_collection.delete_many({})
    print(f"Deleted {result.deleted_count} records.")

asyncio.run(delete_all_data())
