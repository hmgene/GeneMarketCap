from fastapi import FastAPI

from app.api.routes.upload import router as upload_router
from app.api.routes.ask import router as ask_router

app = FastAPI()

app.include_router(upload_router)
app.include_router(ask_router)
