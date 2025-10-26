from fastapi import FastAPI
from app.routes import auth_route, account_route
from app.db.base import Base
from app.db.database import engine
from app.utils.logger import logger

app = FastAPI(title="SmartBanking - Accounts & Auth")


Base.metadata.create_all(bind=engine)
logger.info("Database tables ensured")

app.include_router(auth_route.router)
app.include_router(account_route.router)

@app.get("/")
def root():
    return {"message": "SmartBanking API Running"}
