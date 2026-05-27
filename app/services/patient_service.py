from app.schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status

_patients: dict[int, dict] = {}
_next_id: int = 1


def _now() -> datetime:
    return datetime.utcnow()


def get_all_patients(name: Optional[str] = None) -> list[dict]:
    patients = list(_patients.values())
    if name:
        patients = [p for p in patients if name.lower() in p["name"].lower()]
    return patients


def get_patient_by_id(patient_id: int) -> dict:
    patient = _patients.get(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found"
        )
    return patient


def create_patient(data: PatientCreate) -> dict:
    global _next_id

    for p in _patients.values():
        if p["email"] == data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Patient with email {data.email} already exists"
            )

    now = _now()
    patient = {
        "id": _next_id,
        **data.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    _patients[_next_id] = patient
    _next_id += 1
    return patient


def update_patient(patient_id: int, data: PatientUpdate) -> dict:
    patient = get_patient_by_id(patient_id)
    updates = data.model_dump(exclude_none=True)
    patient.update(updates)
    patient["updated_at"] = _now()
    _patients[patient_id] = patient
    return patient


def delete_patient(patient_id: int) -> dict:
    get_patient_by_id(patient_id)
    del _patients[patient_id]
    return {"message": f"Patient {patient_id} deleted"}