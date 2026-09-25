from fastapi import APIRouter

from app.api.v1.endpoints.alerts import router as alerts_router

api_router = APIRouter()
api_router.include_router(alerts_router)
