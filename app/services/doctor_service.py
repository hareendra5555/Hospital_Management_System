from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from typing import Optional


async def get_all_doctors(
    db: AsyncSession,
    specialty: Optional[str] = None,
    is_available: Optional[bool] = None
) -> list[Doctor]:
    query = select(Doctor)
    if specialty:
        query = query.where(Doctor.specialty == specialty)
    if is_available is not None:
        query = query.where(Doctor.is_available == is_available)
    result = await db.execute(query)
    return result.scalars().all()


async def get_doctor_by_id(db: AsyncSession, doctor_id: int) -> Doctor:
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found"
        )
    return doctor


async def create_doctor(db: AsyncSession, data: DoctorCreate) -> Doctor:
    # Check for duplicate email
    result = await db.execute(select(Doctor).where(Doctor.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Doctor with email {data.email} already exists"
        )
    doctor = Doctor(**data.model_dump())
    db.add(doctor)
    await db.flush()   # writes to DB within transaction, gets the auto-generated id
    await db.refresh(doctor)  # reloads from DB — gets created_at, updated_at
    return doctor


async def update_doctor(db: AsyncSession, doctor_id: int, data: DoctorUpdate) -> Doctor:
    doctor = await get_doctor_by_id(db, doctor_id)
    updates = data.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(doctor, field, value)
    await db.flush()
    await db.refresh(doctor)
    return doctor


async def delete_doctor(db: AsyncSession, doctor_id: int) -> dict:
    doctor = await get_doctor_by_id(db, doctor_id)
    doctor.is_available = False
    await db.flush()
    return {"message": f"Doctor {doctor_id} deactivated successfully"}