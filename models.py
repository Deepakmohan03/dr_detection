from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from dbb import Base
from sqlalchemy.orm import relationship


# Doctor model
class Doctor(Base):
    __tablename__ = 'doctor'
    id = Column(String, primary_key=True)  # Email as the primary key
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    # Optionally, define the reverse relationship to Patient model
    patients = relationship("Patient", back_populates="doctor")

# Patient model
class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # Severity level (No DR, Mild, Moderate, Severe, Proliferate)
    doctor_id = Column(String, ForeignKey('doctor.id'), nullable=False)  # Required field for doctor association

    doctor = relationship("Doctor", back_populates="patients")  # Relationship with Doctor model
