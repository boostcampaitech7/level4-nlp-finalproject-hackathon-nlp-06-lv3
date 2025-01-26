from fastapi import APIRouter, Depends

from server.dependencies.session import get_user_id_from_session
from server.service import report_service

# Initialize router
report_router = APIRouter(prefix="/reports", tags=["Reports"])


@report_router.get("/")
async def get_reports(user_id: int = Depends(get_user_id_from_session)):
    return await report_service.get_reports(user_id)
