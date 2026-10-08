from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="PENDING")
    total = Column(Integer, default=0)
    successful = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    certificates = relationship(
        "Certificate",
        back_populates="job"
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))

    recipient_name = Column(String)
    recipient_email = Column(String)

    status = Column(String, default="PENDING")
    file_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)

    job = relationship(
        "Job",
        back_populates="certificates"
    )