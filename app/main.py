from fastapi import FastAPI
from .routers import user, library
from .database.base import engine
from .database.models import user as user_model

app = FastAPI()
user_model.Base.metadata.create_all(engine)


app.include_router(library.router)
app.include_router(user.router)
