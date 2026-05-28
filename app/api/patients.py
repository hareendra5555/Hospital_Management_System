from fastapi import APIRouter, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.services import patient_service
from app.core.database import get_db

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/", response_model=list[PatientResponse])
async def list_patients(
    name: Optional[str] = Query(None, description="Search by patient name"),
    db: AsyncSession = Depends(get_db),
):
    return await patient_service.get_all_patients(db, name=name)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    return await patient_service.get_patient_by_id(db, patient_id)


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(data: PatientCreate, db: AsyncSession = Depends(get_db)):
    return await patient_service.create_patient(db, data)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: int, data: PatientUpdate, db: AsyncSession = Depends(get_db)):
    return await patient_service.update_patient(db, patient_id, data)


@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    return await patient_service.delete_patient(db, patient_id)