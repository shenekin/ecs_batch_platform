
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey('jobs.id'), index=True)
    index = Column(Integer)
    params = Column(JSON)
    status = Column(String, default='PENDING')
    attempts = Column(Integer, default=0)
    last_error = Column(String, nullable=True)
    cloud_instance_id = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
