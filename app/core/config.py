import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = os.getenv("SERVER_DATABASE_URL",'postgresql://testing_postgres_oujx_user:JpWXaMWrkhYSqYEbrlViJx0yzRpFbuzu@dpg-d3tld52li9vc73bg35j0-a.oregon-postgres.render.com/SmartBankingApplication')
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
MIN_INITIAL_DEPOSIT = float(os.getenv("MIN_INITIAL_DEPOSIT", "1000"))
