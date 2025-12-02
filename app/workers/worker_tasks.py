from app.adapters.cloud_adapter_factory import CloudAdapterFactory
from app.db.repositories.task_repo import TaskRepo
from app.errors import TransientError, PermanentError
from app.limiter import limiter
from app.utils.retry import retry_backoff
from app.celery_app import celery_app

@celery_app.task(name="worker.create_instance", bind=True)
def create_instance(self, task_id):
    task = TaskRepo.get(task_id)
    limiter.acquire(task.tenant)
    try:
        adapter = CloudAdapterFactory.get(task.cloud)
        result = adapter.create_instance(task.params)
        TaskRepo.mark_success(task_id, result)
    except TransientError:
        self.retry(countdown=retry_backoff(self.request.retries))
    except PermanentError as e:
        TaskRepo.mark_failed(task_id, str(e))from app.celery_app import celery_app


