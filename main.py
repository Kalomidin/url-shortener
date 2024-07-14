from fastapi import FastAPI
import repository.database as database
import url_shortener

app = FastAPI()

database.Base.metadata.create_all(bind=database.engine)
app.include_router(url_shortener.router)
