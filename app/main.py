from fastapi import FastAPI
from .routers import user, library

app = FastAPI()


app.include_router(library.router)
app.include_router(user.router)
