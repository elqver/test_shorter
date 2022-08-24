from fastapi import FastAPI
from user_router import user_router
from shorter_router import shorter_router

app = FastAPI()
app.include_router(user_router)
app.include_router(shorter_router)
