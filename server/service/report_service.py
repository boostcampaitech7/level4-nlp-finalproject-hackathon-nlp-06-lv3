from server._core.errors.exceptions.custom_exception import CustomException
from server._core.errors.exceptions.error_code import ErrorCode
from server.database.connection import database
from server.models.user import User
from server.schemas import report_request, report_response


async def get_reports(user: User, page: int, limit: int):
    offset = (page - 1) * limit

    reports = await database.fetch_all(
        ("SELECT * FROM report_temp_tb WHERE user_id = :user_id ORDER BY date DESC LIMIT :limit OFFSET :offset"),
        {
            "user_id": user.id,
            "limit": limit,
            "offset": offset,
        },
    )
    return report_response.TempReportsDto(reports)


async def set_reports(user: User, report_id: int, report_dto: report_request.ReportDto):
    report_owner_id = await database.fetch_one(
        ("SELECT user_id FROM report_temp_tb WHERE id=:report_id"),
        {"report_id": report_id},
    )
    if not report_owner_id:
        raise CustomException(ErrorCode.NOT_FOUND_DATA)
    if report_owner_id["user_id"] != user.id:
        raise CustomException(ErrorCode.PERMISSION_DENIED)

    await database.execute(
        ("UPDATE report_temp_tb SET content=:content WHERE id=:report_id"),
        {"content": report_dto.content, "report_id": report_id},
    )
