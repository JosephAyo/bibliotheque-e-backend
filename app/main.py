from fastapi import FastAPI
from .routers import user, library
from .database.base import engine
from .database.models import user as user_model
from .database.models import role as role_model
from .database.models import permission as permission_model
from .database.models import user_role_association as user_role_association_model
from .database.models import role_permission_association as role_permission_association_model

app = FastAPI()
user_model.Base.metadata.create_all(engine)
role_model.Base.metadata.create_all(engine)
permission_model.Base.metadata.create_all(engine)
user_role_association_model.Base.metadata.create_all(engine)
role_permission_association_model.Base.metadata.create_all(engine)


app.include_router(library.router)
app.include_router(user.router)
