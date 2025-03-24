from fastapi import FastAPI, HTTPException
import httpx
import motor.motor_asyncio
from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
# Serve Static Frontend Files
app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend")
# ✅ MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "cve_db"
COLLECTION_NAME = "cves"

if not MONGO_URI:
    raise ValueError("⚠️ MONGO_URI is missing. Set it in .env file.")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
cve_collection = db[COLLECTION_NAME]

# ✅ NVD API Configuration
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


import logging

# ✅ Enable logging
logging.basicConfig(level=logging.INFO)

@app.get("/sync")
async def sync_cve_data(results_per_page: int = 100, start_index: int = 0):
    """Fetch CVE data from NVD API and store in MongoDB."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(NVD_API_URL, params={"resultsPerPage": results_per_page, "startIndex": start_index})
            data = response.json()

            if "vulnerabilities" in data:
                count = 0  # Track how many CVEs are updated
                for item in data["vulnerabilities"]:
                    cve = item["cve"]
                    cve_id = cve["id"]
                    result = await cve_collection.update_one({"id": cve_id}, {"$set": cve}, upsert=True)
                    if result.upserted_id or result.modified_count > 0:
                        count += 1  # Count updated CVEs

                logging.info(f"✅ {count} CVEs updated in MongoDB.")
                return {"message": f"Data synchronized successfully. {count} CVEs updated."}
            else:
                logging.warning("⚠️ No vulnerabilities found in API response.")
                return {"message": "No new CVE data found."}

    except Exception as e:
        logging.error(f"❌ Error during sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))






# ✅ Function to Convert MongoDB `_id` (ObjectId) to String
def fix_mongo_docs(doc):
    """ Recursively converts ObjectId fields to strings in MongoDB documents """
    if isinstance(doc, list):
        return [fix_mongo_docs(d) for d in doc]
    elif isinstance(doc, dict):
        return {k: fix_mongo_docs(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)  # Convert ObjectId to string
    return doc  # Return normal values unchanged
# ✅ Route to Fetch CVE Data with Filters and Pagination
from pymongo import ASCENDING
from pymongo import ASCENDING
from datetime import datetime, timedelta
from pymongo import ASCENDING
from datetime import datetime, timedelta

@app.get("/cves")
async def get_cves(
    cve_id: Optional[str] = None,
    year: Optional[int] = None,
    min_score: Optional[float] = None,
    last_modified_days: Optional[int] = None,
    page: int = 1,
    results_per_page: int = 10
):
    """Retrieve filtered CVE records from MongoDB."""
    query = {}

    if cve_id:
        query["id"] = {"$regex": cve_id, "$options": "i"}  # ✅ Case-insensitive search

    if year:
        # ✅ Fix: Use regex to match the year in the `published` field
        query["published"] = {"$regex": f"^{year}-"}  # Matches "1999-XX-XX"

    if min_score:
        query["metrics.cvssMetricV2.cvssData.baseScore"] = {"$gte": min_score}

    if last_modified_days:
        # ✅ Fix: Convert last_modified_days to a **string** for MongoDB comparison
        since_date = (datetime.utcnow() - timedelta(days=last_modified_days)).strftime("%Y-%m-%dT%H:%M:%S")
        query["lastModified"] = {"$gte": since_date}  # ✅ Compare as a string

    skip = (page - 1) * results_per_page
    results = await cve_collection.find(query).sort("published", ASCENDING).skip(skip).limit(results_per_page).to_list(length=results_per_page)
    total_records = await cve_collection.count_documents(query)

    # ✅ Convert ObjectId properly before sending response
    fixed_results = fix_mongo_docs(results)

    return JSONResponse(content={"total": total_records, "data": fixed_results})


# ✅ Route to Fetch ALL CVEs (For Debugging)
@app.get("/cves/all")
async def get_all_cves():
    """Retrieve all CVE records from MongoDB."""
    results = await cve_collection.find().to_list(length=None)  # Get all documents
    fixed_results = fix_mongo_docs(results)  # Convert ObjectId before returning
    return JSONResponse(content={"total": len(fixed_results), "data": fixed_results})

@app.get("/")
async def redirect_to_frontend():
    """Redirect root URL to the frontend."""
    return RedirectResponse(url="/static/index.html")


# ✅ Run FastAPI Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
