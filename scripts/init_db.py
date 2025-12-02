
from app.db.base import Base
from app.db.session import engine
# import models so metadata is registered
import app.db.models.job, app.db.models.task

Base.metadata.create_all(bind=engine)
print('DB initialized')
