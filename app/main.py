from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from app.api.v1 import jobs_api, tasks_api, health_api

app = FastAPI(title="ECS Creation Platform")

# Add CORS (allow frontend domains)
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://your-frontend-domain.com"],  # Restrict to my frontend
    # allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Existing router imports
# app.include_router(jobs_api.router, prefix="/api/v1/jobs")
# app.include_router(tasks_api.router, prefix="/api/v1/tasks")
app.include_router(health_api.router, prefix="/api/v1/heals")  # Health check router
app.include_router(jobs_api.router, prefix="/api/v1/jobs")
