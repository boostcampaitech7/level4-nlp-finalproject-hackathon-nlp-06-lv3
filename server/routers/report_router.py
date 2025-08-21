from fastapi import APIRouter, Depends

from server._core.dependencies.session import get_user_id_from_session
from server._core.utils.api_response import ApiResponse
from server.models.user import User
from server.schemas import report_request, report_response
from server.service import report_service

# Initialize router
report_router = APIRouter(prefix="/reports", tags=["Reports"])


@report_router.get("/temp")
async def get_reports_temp(
    user: User = Depends(get_user_id_from_session), page: int = 1, limit: int = 20
) -> ApiResponse[report_response.TempReportsDto]:
    return ApiResponse.success(await report_service.get_reports(user, page, limit))


@report_router.put("/temp/{report_id}")
async def put_reports_temp(
    report_id: int, report_dto: report_request.ReportDto, user: User = Depends(get_user_id_from_session)
) -> ApiResponse:
    await report_service.set_reports(user, report_id, report_dto)
    return ApiResponse.success()
