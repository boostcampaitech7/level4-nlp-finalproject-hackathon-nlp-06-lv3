from typing import Optional

from pydantic import BaseModel


class GoogleAuthDto(BaseModel):
    code: str
    redirect_uri: str


class ProfileUpdateDto(BaseModel):
    upstage_api_key: Optional[str] = None
