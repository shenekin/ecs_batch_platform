
import uuid
from app.db.models.job import Job

class JobRepo:
    @staticmethod
    def create(db, submitter, total, meta=None):
        job = Job(id=str(uuid.uuid4()), submitter=submitter, total=total, meta=meta)
        db.add(job)
        db.commit()
        return job
