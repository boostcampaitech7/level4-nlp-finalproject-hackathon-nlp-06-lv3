from fastapi import APIRouter, Depends

from server._core.utils.api_response import ApiResponse
from server.dependencies.session import get_user_id_from_session
from server.schemas import report_response
from server.service import report_service

# Initialize router
report_router = APIRouter(prefix="/reports", tags=["Reports"])


@report_router.get("/temp")
async def get_reports_temp(
    user_id: int = Depends(get_user_id_from_session), page: int = 1, limit: int = 20
) -> ApiResponse[report_response.TempReportsDto]:
    return ApiResponse.success(await report_service.get_reports(user_id, page, limit))
