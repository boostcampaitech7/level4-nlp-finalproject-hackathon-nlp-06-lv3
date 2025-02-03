from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int | None = None  # Auto-increment, so it can be optional
    google_id: str
    access_token: str
    refresh_token: str
    expiry: datetime
    created_at: datetime | None = None  # Defaults to current timestamp in DB
