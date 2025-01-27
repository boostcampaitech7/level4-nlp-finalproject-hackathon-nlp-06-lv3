from pydantic import BaseModel


class IsLoginDto(BaseModel):
    is_login: bool
    user_id: int

    def __init__(self, user_id: int):
        super().__init__(is_login=bool(user_id), user_id=user_id)


class GoogleAuthDto(BaseModel):
    user_id: int


class LogoutDto(BaseModel):
    message: str


class GoogleProfileDto(BaseModel):
    google_id: str
    email: str
    name: str
    given_name: str
    family_name: str
    picture: str

    def __init__(self, json_response: dict):
        print(json_response)
        super().__init__(
            google_id=json_response["id"],
            email=json_response["email"],
            name=json_response["name"],
            given_name=json_response["given_name"],
            family_name=json_response["family_name"],
            picture=json_response["picture"],
        )


class GoogleCallbackDto(BaseModel):
    code: str
