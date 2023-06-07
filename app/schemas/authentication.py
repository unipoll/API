from pydantic import BaseModel


class LoginOutput(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires: int = 3600
