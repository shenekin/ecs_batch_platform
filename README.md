
ECS Batch Platform - Skeleton
-----------------------------
This is a starter codebase for the Batch ECS Creation platform.
Contains:
- FastAPI app (app/main.py)
- SQLAlchemy models (app/db/models)
- Alembic migrations (alembic/)
- Celery worker (app/workers)
- Docker Compose for local testing (docker/docker-compose.yml)
- K8s manifests (k8s/)
- Prometheus scrape config and Grafana dashboard placeholders
- Postman collection for API testing

To run locally (dev):
1. Install dependencies from requirements.txt
2. Start postgres and redis (docker-compose)
3. Initialize DB: python scripts/init_db.py
4. Start API: uvicorn app.main:app --reload
5. Start worker: celery -A app.workers.celery_app.celery worker --loglevel=info


uvicorn app.main:app --host 0.0.0.0 --port 8080

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

APIS:
http://127.0.0.1:8080/api/v1/jobs/ecs_creation/json
http://127.0.0.1:8080/api/v1/jobs/ecs_creation/file


