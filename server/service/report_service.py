from server.database.connection import database
from server.models.user import User
from server.schemas import report_response


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


async def set_reports(report_id: int, content: str) -> int:
    updated: int = await database.execute(
        ("UPDATE report_temp_tb Set content=:content WHERE report_id=:report_id"),
        {"content": content, "report_id": report_id},
    )
    return updated
