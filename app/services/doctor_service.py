from app.schemas.doctor import DoctorCreate, DoctorUpdate
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status

# Temporary in-memory store
# In Phase 2 this entire block gets replaced by SQLAlchemy DB calls
# Nothing outside this file needs to change
_doctors: dict[int, dict] = {}
_next_id: int = 1

def _now() -> datetime:
    return datetime.utcnow()

def get_all_doctors(
        speciality: Optional[str] = None,
        is_available: Optional[bool] = None,
) -> list[dict]:
    doctors = list(_doctors.values())

    if speciality:
        doctors = [d for d in doctors if d["speciality"] == speciality]
    if is_available is not None:
        doctors = [d for d in doctors if d["is_available"] == is_available]
    
    return doctors

def get_doctor_by_id(doctor_id: int) -> dict:
    doctor = _doctors.get(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found"
        )
    return doctor

def create_doctor(data: DoctorCreate) -> dict:
    global _next_id

    for doc in _doctors.values():
        if doc["email"] == data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Doctor with email {data.email} already exists"
            )

    now = _now()
    doctor = {
        "id": _next_id,
        **data.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    _doctors[_next_id] = doctor
    _next_id += 1
    return doctor

def update_doctor(doctor_id: int, data: DoctorUpdate) -> dict:
    doctor = get_doctor_by_id(doctor_id)

    updates = data.model_dump(exclude_none=True)
    doctor.update(updates)
    doctor["updated_at"] = _now()
    _doctors[doctor_id] = doctor
    return doctor

def delete_doctor(doctor_id: int) -> dict:
    get_doctor_by_id(doctor_id)
    _doctors[doctor_id]["is_available"] = False
    _doctors[doctor_id]["updated_at"] = _now()
    return {"message": f"Doctor {doctor_id} deactivated successfully"}