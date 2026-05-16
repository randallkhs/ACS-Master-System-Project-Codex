from fastapi import APIRouter

from app.api.v1.routes import dashboard, dispatch, health, jobs, review, technicians

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(technicians.router, prefix="/technicians", tags=["technicians"])
api_router.include_router(review.router, prefix="/review", tags=["manual-review"])
api_router.include_router(dispatch.router, prefix="/dispatch", tags=["dispatch"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
