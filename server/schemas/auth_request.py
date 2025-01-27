from pydantic import BaseModel


class GoogleAuthDto(BaseModel):
    code: str
    redirect_uri: str
