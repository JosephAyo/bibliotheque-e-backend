from fastapi import FastAPI
from .routers import library, user
from .database.base import engine
from .database.models import user as user_model
from .database.models import role as role_model
from .database.models import permission as permission_model
from .database.models import user_role_association as user_role_association_model
from .database.models import role_permission_association as role_permission_association_model
from .database.models import suspension_log as suspension_log_model
from .database.models import book as book_model
from .database.models import genre as genre_model
from .database.models import book_genre_association as book_genre_association_model
from .database.models import check_in_out as check_in_out_model
from .database.models import notification as notification_model
from .database.models import faq as faq_model
from .database.models import app_log as app_log_model

app = FastAPI()
user_model.Base.metadata.create_all(engine)
role_model.Base.metadata.create_all(engine)
permission_model.Base.metadata.create_all(engine)
user_role_association_model.Base.metadata.create_all(engine)
role_permission_association_model.Base.metadata.create_all(engine)
suspension_log_model.Base.metadata.create_all(engine)
book_model.Base.metadata.create_all(engine)
genre_model.Base.metadata.create_all(engine)
book_genre_association_model.Base.metadata.create_all(engine)
check_in_out_model.Base.metadata.create_all(engine)
notification_model.Base.metadata.create_all(engine)
faq_model.Base.metadata.create_all(engine)
app_log_model.Base.metadata.create_all(engine)


app.include_router(library.router)
app.include_router(user.router)
