from pydantic import BaseModel


class JWTTokenResponseModel(BaseModel):
    access_token: str
    token_type: str = "Bearer"
