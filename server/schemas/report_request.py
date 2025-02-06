from pydantic import BaseModel


class ReportDto(BaseModel):
    content: str
