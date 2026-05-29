from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Role drives all authorization decisions
    # Values: "admin", "doctor", "receptionist"
    role = Column(String(20), nullable=False, default="receptionist")

    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Links a doctor-role user to their Doctor record
    # NULL for admin and receptionist users
    doctor_id = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())