from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatus
from app.services import doctor_service, patient_service
from typing import Optional


async def get_all_appointments(
    db: AsyncSession,
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    appt_status: Optional[AppointmentStatus] = None
) -> list[Appointment]:
    query = select(Appointment)
    if doctor_id:
        query = query.where(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.where(Appointment.patient_id == patient_id)
    if appt_status:
        query = query.where(Appointment.status == appt_status)
    result = await db.execute(query)
    return result.scalars().all()


async def get_appointment_by_id(db: AsyncSession, appt_id: int) -> Appointment:
    result = await db.execute(select(Appointment).where(Appointment.id == appt_id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appt_id} not found"
        )
    return appt


async def create_appointment(db: AsyncSession, data: AppointmentCreate) -> Appointment:
    doctor = await doctor_service.get_doctor_by_id(db, data.doctor_id)
    await patient_service.get_patient_by_id(db, data.patient_id)

    if not doctor.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doctor {data.doctor_id} is not currently available"
        )

    appt = Appointment(
        **data.model_dump(),
        status=AppointmentStatus.SCHEDULED
    )
    db.add(appt)
    await db.flush()
    await db.refresh(appt)

    # Phase 4 hook — SQS message goes here
    # await sqs_service.send_appointment_created(appt)

    return appt


async def update_appointment(db: AsyncSession, appt_id: int, data: AppointmentUpdate) -> Appointment:
    appt = await get_appointment_by_id(db, appt_id)
    updates = data.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(appt, field, value)
    await db.flush()
    await db.refresh(appt)
    return appt


async def cancel_appointment(db: AsyncSession, appt_id: int) -> Appointment:
    appt = await get_appointment_by_id(db, appt_id)
    if appt.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed appointment"
        )
    appt.status = AppointmentStatus.CANCELLED
    await db.flush()
    await db.refresh(appt)
    return appt