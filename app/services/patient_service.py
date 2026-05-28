from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate
from typing import Optional


async def get_all_patients(
    db: AsyncSession,
    name: Optional[str] = None
) -> list[Patient]:
    query = select(Patient)
    if name:
        query = query.where(Patient.name.ilike(f"%{name}%"))
    result = await db.execute(query)
    return result.scalars().all()


async def get_patient_by_id(db: AsyncSession, patient_id: int) -> Patient:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found"
        )
    return patient


async def create_patient(db: AsyncSession, data: PatientCreate) -> Patient:
    result = await db.execute(select(Patient).where(Patient.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Patient with email {data.email} already exists"
        )
    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.flush()
    await db.refresh(patient)
    return patient


async def update_patient(db: AsyncSession, patient_id: int, data: PatientUpdate) -> Patient:
    patient = await get_patient_by_id(db, patient_id)
    updates = data.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(patient, field, value)
    await db.flush()
    await db.refresh(patient)
    return patient


async def delete_patient(db: AsyncSession, patient_id: int) -> dict:
    patient = await get_patient_by_id(db, patient_id)
    await db.delete(patient)
    return {"message": f"Patient {patient_id} deleted"}