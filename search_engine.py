from pymongo import MongoClient
from dotenv import load_dotenv
import os
from openai import OpenAI
import numpy as np

# load API key
load_dotenv()
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["Fraud_db"]
collection = db["Cases"]
print("Connected to MongoDB!")

#Function to Generate embedding 
def get_embedding(text):
    text = str(text).replace("\n","")
    response = client_openai.embeddings.create(
        model="text-embedding-3-small",
        input = [text]
    )
    return response.data[0].embedding

#Function to compute consine similairty 
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

#Function to assign risk level
def get_risk_level(score):
    if score >= 0.70:
        return "HIGH"
    elif score >= 0.50:
        return "MEDIUM"
    else:
        return "LOW"
    

#Function to create the search engine 
def search_similar_cases(query_text, fraud_type=None, country=None, min_score=0):
        
 #1. convert query into embedding

    query_embedding = get_embedding(query_text)
    results = []

    query_filter = {"embedding":{"$exists": True, "$ne": None}}

    if fraud_type:
        query_filter["type"] = fraud_type

    if country:
        query_filter["country"] = country

    for doc in collection.find(query_filter):
        score = cosine_similarity(query_embedding, doc["embedding"])

        #Skip weak matches
        if score < min_score:
            continue

        results.append({
             "case_id": doc.get("case_id", "UNKNOWN"),
             "description": doc.get("description",""),
             "type": doc.get("type",""),
             "country": doc.get("country",""),
             "score": score,
             "risk_level": get_risk_level(score),
             "explanation": generate_explanation(
                 query_text,
                 doc.get("description","")
                )
            })

    # sort by similarity (highest first)
    results = sorted(results, key=lambda x: x["score"], reverse = True)

    return results
    

#Explain why query results are related to the query
def generate_explanation(query, case_description):

    prompt = f"""
    An investigator searched for:
    {query}

    Fraud case:
    {case_description}

    In one sentence, explain why this fraud case is relevant.
    """

    response = client_openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
   
