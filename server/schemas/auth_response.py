from typing import Optional

from pydantic import BaseModel

from server.models.user import User


class IsLoginDto(BaseModel):
    is_login: bool
    user_id: Optional[int]

    def __init__(self, user_id: int):
        super().__init__(is_login=bool(user_id), user_id=user_id)


class GoogleAuthDto(BaseModel):
    user_id: int


class ProfileDto(BaseModel):
    upstage_api_key: Optional[str]
    google_id: str
    email: str
    name: str
    given_name: str
    family_name: str
    picture: str

    def __init__(self, user: User, json_response: dict):
        super().__init__(
            id=user.id,
            upstage_api_key=user.upstage_api_key,
            google_id=json_response.get("id"),
            email=json_response.get("email", ""),
            name=json_response.get("name", ""),
            given_name=json_response.get("given_name", ""),
            family_name=json_response.get("family_name", ""),
            picture=json_response.get("picture", ""),
        )


class GoogleCallbackDto(BaseModel):
    code: str
