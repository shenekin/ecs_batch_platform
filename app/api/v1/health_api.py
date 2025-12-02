from fastapi import APIRouter

router = APIRouter(tags=["Health"])  # Optional: Add tag for Swagger Docs

# Use empty string "" instead of "/health" (prefix handles the path)
@router.get("/health", summary="Check service health")
def health():
    return {"status": "ok"}

