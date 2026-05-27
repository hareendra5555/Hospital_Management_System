from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatus
from app.services import doctor_service, patient_service
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status

_appointments: dict[int, dict] = {}
_next_id: int = 1


def _now() -> datetime:
    return datetime.utcnow()


def get_all_appointments(
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    appt_status: Optional[AppointmentStatus] = None
) -> list[dict]:
    appts = list(_appointments.values())
    if doctor_id:
        appts = [a for a in appts if a["doctor_id"] == doctor_id]
    if patient_id:
        appts = [a for a in appts if a["patient_id"] == patient_id]
    if appt_status:
        appts = [a for a in appts if a["status"] == appt_status]
    return appts


def get_appointment_by_id(appt_id: int) -> dict:
    appt = _appointments.get(appt_id)
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appt_id} not found"
        )
    return appt


def create_appointment(data: AppointmentCreate) -> dict:
    global _next_id

    # Cross-entity validation — both must exist
    doctor = doctor_service.get_doctor_by_id(data.doctor_id)
    patient_service.get_patient_by_id(data.patient_id)

    # Business rule — doctor must be available
    if not doctor["is_available"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doctor {data.doctor_id} is not currently available"
        )

    now = _now()
    appt = {
        "id": _next_id,
        **data.model_dump(),
        "status": AppointmentStatus.SCHEDULED,
        "created_at": now,
        "updated_at": now,
    }
    _appointments[_next_id] = appt
    _next_id += 1

    # Phase 4 hook — SQS message goes here
    # sqs_service.send_appointment_created(appt)

    return appt


def update_appointment(appt_id: int, data: AppointmentUpdate) -> dict:
    appt = get_appointment_by_id(appt_id)
    updates = data.model_dump(exclude_none=True)
    appt.update(updates)
    appt["updated_at"] = _now()
    _appointments[appt_id] = appt
    return appt


def cancel_appointment(appt_id: int) -> dict:
    appt = get_appointment_by_id(appt_id)

    if appt["status"] == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed appointment"
        )

    appt["status"] = AppointmentStatus.CANCELLED
    appt["updated_at"] = _now()
    _appointments[appt_id] = appt
    return appt