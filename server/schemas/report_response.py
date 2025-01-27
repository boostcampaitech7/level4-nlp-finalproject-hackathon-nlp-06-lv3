from datetime import date, datetime

from pydantic import BaseModel


class TempReportsDto(BaseModel):
    class Report(BaseModel):
        id: int
        content: str
        date: date
        refresh_time: datetime

    reports: list[Report]

    def __init__(self, reports: list[dict]):
        super().__init__(
            reports=[
                self.Report(
                    id=report["id"],
                    content=report["content"],
                    date=report["date"],
                    refresh_time=report["refresh_time"],
                )
                for report in reports
            ]
        )
