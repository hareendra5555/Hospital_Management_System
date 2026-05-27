from fastapi import APIRouter, status, Query
from typing import Optional
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentStatus
)
from app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(
    doctor_id: Optional[int] = Query(None, description="Filter by doctor"),
    patient_id: Optional[int] = Query(None, description="Filter by patient"),
    appt_status: Optional[AppointmentStatus] = Query(None, description="Filter by status"),
):
    return appointment_service.get_all_appointments(
        doctor_id=doctor_id,
        patient_id=patient_id,
        appt_status=appt_status
    )


@router.get("/{appt_id}", response_model=AppointmentResponse)
def get_appointment(appt_id: int):
    return appointment_service.get_appointment_by_id(appt_id)


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(data: AppointmentCreate):
    return appointment_service.create_appointment(data)


@router.put("/{appt_id}", response_model=AppointmentResponse)
def update_appointment(appt_id: int, data: AppointmentUpdate):
    return appointment_service.update_appointment(appt_id, data)


@router.delete("/{appt_id}")
def cancel_appointment(appt_id: int):
    return appointment_service.cancel_appointment(appt_id)