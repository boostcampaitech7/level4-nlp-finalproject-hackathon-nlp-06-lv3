from server.database.connection import database


async def get_reports(user_id: int, page: int, limit: int):
    offset = (page - 1) * limit

    reports = await database.fetch_all(
        ("SELECT * FROM report_temp_tb WHERE user_id = :user_id ORDER BY date DESC LIMIT :limit OFFSET :offset"),
        {
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
        },
    )
    return {
        "reports": [
            {
                "id": report["id"],
                "content": report["content"],
                "date": report["date"],
                "refresh_time": report["refresh_time"],
            }
            for report in reports
        ]
    }
