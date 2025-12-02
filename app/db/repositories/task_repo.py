
import uuid
from app.db.models.task import Task

class TaskRepo:
    @staticmethod
    def bulk_create(db, job_id, instances):
        tasks = []
        for idx, inst in enumerate(instances):
            t = Task(id=str(uuid.uuid4()), job_id=job_id, index=idx, params=inst.dict())
            db.add(t)
            tasks.append(t)
        db.commit()
        return tasks

    @staticmethod
    def list_by_job(job_id, db):
        return db.query(Task).filter(Task.job_id==job_id).all()

    @staticmethod
    def mark_success(db, task_id, instance_id):
        t = db.query(Task).get(task_id)
        t.status = 'SUCCESS'
        t.cloud_instance_id = instance_id
        db.commit()
        return t
