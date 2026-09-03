# import os
# import httpx
# from fastapi import FastAPI, HTTPException, status
# from fastapi.middleware.cors import CORSMiddleware
# from datetime import datetime
# from bson import ObjectId

# from database import leads_collection
# from schemas import LeadCreate

# app = FastAPI(title="SnapServe Lead Connect API")

# # Enable CORS for React Frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# SNAPSERVE_API_KEY = os.getenv("SNAPSERVE_API_KEY")
# SNAPSERVE_AGENT_ID = os.getenv("SNAPSERVE_AGENT_ID")
# SNAPSERVE_API_URL = os.getenv("SNAPSERVE_API_URL")

# @app.post("/api/leads", status_code=status.HTTP_201_CREATED)
# async def create_lead_and_trigger_call(lead: LeadCreate):
#     # 1. Save lead to MongoDB
#     lead_dict = lead.model_dump()
#     lead_dict["status"] = "PENDING"
#     lead_dict["created_at"] = datetime.utcnow()
    
#     result = await leads_collection.insert_one(lead_dict)
#     lead_id = str(result.inserted_id)

#     # 2. Build SnapServe Request
#     payload = {
#         "agent_id": SNAPSERVE_AGENT_ID,
#         "recipient_phone": lead.phone_number,
#         "metadata": {
#             "lead_id": lead_id,
#             "name": lead.name,
#             "service_interest": lead.service_interest
#         }
#     }
#     headers = {
#         "Authorization": f"Bearer {SNAPSERVE_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             # Send request using SNAPSERVE_API_URL from .env
#             response = await client.post(
#                 SNAPSERVE_API_URL, 
#                 json=payload, 
#                 headers=headers, 
#                 timeout=10.0
#             )
            
#             # Print response to terminal for debugging
#             print(f"--- SnapServe API Request to: {SNAPSERVE_API_URL} ---")
#             print(f"Response Status: {response.status_code}")
#             print(f"Response Body: {response.text}")

#             if response.status_code in [200, 201]:
#                 call_data = response.json()
#                 call_id = call_data.get("call_id") or call_data.get("id")
                
#                 await leads_collection.update_one(
#                     {"_id": ObjectId(lead_id)},
#                     {"$set": {"status": "CALL_INITIATED", "snapserve_call_id": call_id}}
#                 )
#                 return {
#                     "message": "Lead saved and call initiated successfully!",
#                     "lead_id": lead_id,
#                     "call_id": call_id
#                 }
#             else:
#                 await leads_collection.update_one(
#                     {"_id": ObjectId(lead_id)},
#                     {"$set": {"status": "CALL_FAILED"}}
#                 )
#                 raise HTTPException(
#                     status_code=response.status_code, 
#                     detail=f"SnapServe API Error ({response.status_code}): {response.text}"
#                 )
#         except HTTPException:
#             raise
#         except Exception as e:
#             await leads_collection.update_one(
#                 {"_id": ObjectId(lead_id)},
#                 {"$set": {"status": "FAILED"}}
#             )
#             raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/webhooks/snapserve")
# async def snapserve_webhook(data: dict):
#     call_id = data.get("call_id")
#     call_status = data.get("status")
    
#     if call_id:
#         await leads_collection.update_one(
#             {"snapserve_call_id": call_id},
#             {"$set": {"status": f"CALL_{call_status.upper()}", "call_details": data}}
#         )

#     return {"status": "ok"}

import os
import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from bson import ObjectId

from database import leads_collection
from backend.src.schemas import LeadCreate

app = FastAPI(title="SnapServe Lead Connect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SNAPSERVE_API_KEY = os.getenv("SNAPSERVE_API_KEY")
SNAPSERVE_API_URL = os.getenv("SNAPSERVE_API_URL")

@app.post("/api/leads", status_code=status.HTTP_201_CREATED)
async def create_lead_and_trigger_call(lead: LeadCreate):
    # 1. Save lead to MongoDB Atlas
    lead_dict = lead.model_dump()
    lead_dict["status"] = "PENDING"
    lead_dict["created_at"] = datetime.utcnow()
    
    result = await leads_collection.insert_one(lead_dict)
    lead_id = str(result.inserted_id)

    # 2. Build payload for SnapServe Campaign Webhook
    payload = {
        "name": lead.name,
        "phone": lead.phone_number,
        "phone_number": lead.phone_number,
        "email": lead.email,
        "service_interest": lead.service_interest,
        "metadata": {
            "lead_id": lead_id,
            "service_interest": lead.service_interest
        }
    }
    
    headers = {
        "Authorization": f"Bearer {SNAPSERVE_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\n[DEBUG] Dispatching lead to Campaign Webhook: {SNAPSERVE_API_URL}")
    print(f"[DEBUG] Payload: {payload}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SNAPSERVE_API_URL, 
                json=payload, 
                headers=headers, 
                timeout=10.0
            )
            
            print(f"[DEBUG] Webhook Response Status: {response.status_code}")
            print(f"[DEBUG] Webhook Response Body: {response.text}\n")

            if response.status_code in [200, 201, 202]:
                call_data = {}
                try:
                    call_data = response.json()
                except Exception:
                    call_data = {"response": response.text}

                call_id = call_data.get("call_id") or call_data.get("id") or call_data.get("lead_id", "queued")
                
                await leads_collection.update_one(
                    {"_id": ObjectId(lead_id)},
                    {"$set": {"status": "CALL_INITIATED", "snapserve_call_id": call_id}}
                )
                return {
                    "message": "Lead submitted to campaign successfully!", 
                    "lead_id": lead_id, 
                    "call_id": call_id
                }
            else:
                await leads_collection.update_one(
                    {"_id": ObjectId(lead_id)},
                    {"$set": {"status": "CALL_FAILED"}}
                )
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"SnapServe Webhook Error ({response.status_code}): {response.text}"
                )

        except HTTPException:
            raise
        except Exception as e:
            await leads_collection.update_one(
                {"_id": ObjectId(lead_id)},
                {"$set": {"status": "FAILED"}}
            )
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhooks/snapserve")
async def snapserve_webhook(data: dict):
    call_id = data.get("call_id") or data.get("id")
    call_status = data.get("status")
    
    if call_id and call_status:
        await leads_collection.update_one(
            {"snapserve_call_id": call_id},
            {"$set": {"status": f"CALL_{call_status.upper()}", "call_details": data}}
        )
    return {"status": "ok"}