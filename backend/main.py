from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database import create_db_and_tables
from routers import auth, films



app = FastAPI()
app.include_router(auth.router)
app.include_router(films.router)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    create_db_and_tables()

