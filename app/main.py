import uvicorn
from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.game import router as game_router
from app.routers.user import router as user_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(game_router, prefix="/games", tags=["games"])
app.include_router(user_router, prefix="/user", tags=["user"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
