from fastapi import APIRouter, status, Query
from typing import Optional
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from app.services import doctor_service

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("/", response_model=list[DoctorResponse])
def list_doctors(
    speciality: Optional[str] = Query(None, description="Filter by Speciality"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
):
    return doctor_service.get_all_doctors(
        speciality=speciality,
        is_available=is_available
    )

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int):
    return doctor_service.get_doctor_by_id(doctor_id)

@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(data: DoctorCreate):
    return doctor_service.create_doctor(data)

@router.post("/", response_model=DoctorResponse)
def update_doctor(doctor_id: int, data: DoctorUpdate):
    return doctor_service.update_doctor(doctor_id, data)

@router.delete("/{doctor_id}")
def delete_router(doctor_id: int):
    return doctor_service.delete_doctor(doctor_id)