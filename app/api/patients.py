from fastapi import APIRouter, status, Query
from typing import Optional
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.services import patient_service

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/", response_model=list[PatientResponse])
def list_patients(
    name: Optional[str] = Query(None, description="Search by patient name"),
):
    return patient_service.get_all_patients(name=name)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int):
    return patient_service.get_patient_by_id(patient_id)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(data: PatientCreate):
    return patient_service.create_patient(data)


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, data: PatientUpdate):
    return patient_service.update_patient(patient_id, data)


@router.delete("/{patient_id}")
def delete_patient(patient_id: int):
    return patient_service.delete_patient(patient_id)