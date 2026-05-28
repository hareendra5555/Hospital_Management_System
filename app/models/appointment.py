from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(500), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default="scheduled", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships — lets you do appointment.doctor to get the Doctor object
    doctor = relationship("Doctor", lazy="selectin")
    patient = relationship("Patient", lazy="selectin")