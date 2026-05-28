from fastapi import APIRouter, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.schemas.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from app.services import doctor_service
from app.core.database import get_db

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=list[DoctorResponse])
async def list_doctors(
    specialty: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await doctor_service.get_all_doctors(db, specialty=specialty, is_available=is_available)


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: int, db: AsyncSession = Depends(get_db)):
    return await doctor_service.get_doctor_by_id(db, doctor_id)


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(data: DoctorCreate, db: AsyncSession = Depends(get_db)):
    return await doctor_service.create_doctor(db, data)


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(doctor_id: int, data: DoctorUpdate, db: AsyncSession = Depends(get_db)):
    return await doctor_service.update_doctor(db, doctor_id, data)


@router.delete("/{doctor_id}")
async def delete_doctor(doctor_id: int, db: AsyncSession = Depends(get_db)):
    return await doctor_service.delete_doctor(db, doctor_id)