from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: Optional[int] = None
    google_id: str
    access_token: str
    refresh_token: str
    expiry: datetime
    upstage_api_key: Optional[str] = None
    created_at: Optional[datetime] = None
