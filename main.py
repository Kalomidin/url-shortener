from fastapi import FastAPI
from repository import models
from repository.database import engine
import url_hasher

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(url_hasher.router)
