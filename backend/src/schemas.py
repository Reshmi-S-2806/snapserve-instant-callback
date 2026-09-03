from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class LeadCreate(BaseModel):
    name: str = Field(..., example="Jane Doe")
    phone_number: str = Field(..., example="+1234567890")
    email: Optional[EmailStr] = None
    service_interest: str = Field(..., example="Web Development")

class LeadResponse(LeadCreate):
    id: str
    status: str
    snapserve_call_id: Optional[str] = None
    created_at: datetime