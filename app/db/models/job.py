
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    submitter = Column(String, nullable=True)
    status = Column(String, default="PENDING")
    total = Column(Integer, default=0)
    succeeded = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
