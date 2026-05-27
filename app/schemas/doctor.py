from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime

class Specialty(str, Enum):
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    ORTHOPEDICS = "orthopedics"
    PEDIATRICS = "pediatrics"
    GENERAL = "general"
    RADIOLOGY = "radiology"

class DoctorBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    specialty: Specialty
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")
    years_of_experience: int = Field(..., ge=0, le=50)
    is_available: bool = Field(default=True)

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    specialty: Optional[Specialty] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{9,14}$")
    years_of_experience: Optional[int] = Field(None, ge=0, le=50)
    is_available: Optional[bool] = None

class DoctorResponse(DoctorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True