from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class LabTemplate(Base):
    __tablename__ = "lab_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    #consider adding category
    service_id = Column(Integer, index=True)
    fields = Column(JSONB, nullable=False) 
    created_by = Column(Integer, nullable=True)
    facility_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# class LabResult(Base):
#     __tablename__ = "lab_results"

#     id = Column(Integer, primary_key=True, index=True)
#     appointment_id = Column(Integer, index=True)
#     service_id = Column(Integer, index=True)
#     sample_id = Column(Integer, index=True)

#     result = Column(Text, nullable=True)           # Human-readable string
#     result_json = Column(JSONB, nullable=True)     # Structured result
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)