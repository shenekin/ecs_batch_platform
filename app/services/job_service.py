
from app.db.repositories.job_repo import JobRepo
from app.db.repositories.task_repo import TaskRepo
from app.workers.celery_app import celery_app

class JobService:
    @staticmethod
    def create_job(req, db):
        job = JobRepo.create(db, submitter=None, total=len(req.instances), meta={})
        tasks = TaskRepo.bulk_create(db, job.id, req.instances)
        # push tasks to celery
        for t in tasks:
            celery_app.send_task('app.workers.worker_tasks.create_instance', args=[t.id])
        return job
