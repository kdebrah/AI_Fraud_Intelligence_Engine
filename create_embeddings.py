from pymongo import MongoClient
from dotenv import load_dotenv
import os
from openai import OpenAI

# load API key
load_dotenv()
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["Fraud_db"]
collection = db["Cases"]
print("Connected to MongoDB!")

#function to Generate embedding 
def get_embedding(text):
    text = str(text).replace("\n","")
    response = client_openai.embeddings.create(
        model="text-embedding-3-small",
        input = [text]
    )
    return response.data[0].embedding

#STEP: Loop through ALL documents 
for doc in collection.find():
    #Skip if already embedded (prevents duplicates)
    if "embedding" in doc and doc["embedding"] is not None:
        print(f"Skipping {doc.get('case_id','UNKNOWN')} (already has embedding)")
        continue
    
    text = doc.get("description","")
    embedding = get_embedding(text)

    #Save embedding back to MongoDB
    collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"embedding": embedding }}
    )

    print(f"updated {doc.get('case_id', 'UNKNOWN')}")
    
print("All embeddings stored successfully")
    
