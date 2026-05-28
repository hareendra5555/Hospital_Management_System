from fastapi import APIRouter, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentStatus,
)
from app.services import appointment_service
from app.core.database import get_db

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("/", response_model=list[AppointmentResponse])
async def list_appointments(
    doctor_id: Optional[int] = Query(None, description="Filter by doctor"),
    patient_id: Optional[int] = Query(None, description="Filter by patient"),
    appt_status: Optional[AppointmentStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    return await appointment_service.get_all_appointments(
        db,
        doctor_id=doctor_id,
        patient_id=patient_id,
        appt_status=appt_status,
    )


@router.get("/{appt_id}", response_model=AppointmentResponse)
async def get_appointment(appt_id: int, db: AsyncSession = Depends(get_db)):
    return await appointment_service.get_appointment_by_id(db, appt_id)


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(data: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    return await appointment_service.create_appointment(db, data)


@router.put("/{appt_id}", response_model=AppointmentResponse)
async def update_appointment(appt_id: int, data: AppointmentUpdate, db: AsyncSession = Depends(get_db)):
    return await appointment_service.update_appointment(db, appt_id, data)


@router.delete("/{appt_id}")
async def cancel_appointment(appt_id: int, db: AsyncSession = Depends(get_db)):
    return await appointment_service.cancel_appointment(db, appt_id)