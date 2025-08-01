from pydantic import BaseModel, Field


class UserResponseModel(BaseModel):
    id: int
    username: str
    role_name: str | None
    liked_genres_names: list[str] | None

    class Config:
        from_attributes = True


class UserCreateModel(BaseModel):
    username: str = Field(max_length=25)
    password: str = Field(max_length=25)

    class Config:
        from_attributes = True


class UserCreateResponseModel(BaseModel):
    message: str
    user_id: int


class UserUpdateModel(BaseModel):
    username: str | None = Field(None, max_length=25)
    password: str | None = Field(None, max_length=25)
    role_id: int | None = None
    liked_genre_ids: list[int] | None = None

    class Config:
        from_attributes = True
