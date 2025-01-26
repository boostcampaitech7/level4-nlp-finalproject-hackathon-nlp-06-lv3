from server.database.connection import database


async def get_reports(user_id: int):
    reports = await database.fetch_all("SELECT * FROM report_temp_tb WHERE user_id = :user_id", {"user_id": user_id})
    return {
        "reports": [
            {
                "id": report["id"],
                "content": report["content"],
                "date": report["date"],
                "refresh_time": report["refresh_time"],
            }
            for report in sorted(reports, key=lambda x: x["date"], reverse=True)
        ]
    }
