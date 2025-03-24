import motor.motor_asyncio
import asyncio
from bson import ObjectId

# ✅ MongoDB Connection
MONGO_URI = "mongodb+srv://ratu:ratu123@cluster0.r5gnp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "cve_db"
COLLECTION_NAME = "cves"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
cve_collection = db[COLLECTION_NAME]

# ✅ Function to Convert ObjectId to String
def fix_mongo_docs(doc):
    """ Recursively converts ObjectId fields to strings in MongoDB documents """
    if isinstance(doc, list):
        return [fix_mongo_docs(d) for d in doc]
    elif isinstance(doc, dict):
        return {k: fix_mongo_docs(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)  # Convert ObjectId to string
    return doc

# ✅ Function to Fetch and Print All CVE Data
async def print_all_cves():
    """Fetch and print all CVE records from MongoDB."""
    results = await cve_collection.find().to_list(length=None)  # Get all documents
    fixed_results = fix_mongo_docs(results)  # Convert ObjectId before printing
    
    if not fixed_results:
        print("No CVE data found in the database.")
    else:
        for idx, cve in enumerate(fixed_results, start=1):
            print(f"\n🔹 CVE {idx}:")
            print(cve)

# ✅ Run the Async Function
if __name__ == "__main__":
    asyncio.run(print_all_cves())
