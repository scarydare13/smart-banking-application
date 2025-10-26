import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db import database
from app.core import security as security_module
from app.models.customer import Customer
from app.core.security import hash_password

from app.db.database import engine
from app.utils.logger import logger


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency used by the app
app.dependency_overrides[database.get_db] = override_get_db

# Prevent sending real emails during tests
import app.routes.account_route as account_route_module
account_route_module.send_account_email = lambda *args, **kwargs: None

@pytest.fixture()
def client():
    return TestClient(app)

@pytest.fixture()
def test_user():
    db = SessionLocal()
    # Create a test customer with VERIFIED KYC
    user = Customer(
        full_name="Test User",
        email="testuser@example.com",
        phone_number="+911234567890",
        password_hash=hash_password("Secret123"),
        kyc_status="VERIFIED"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.customer_id
    db.close()
    return user

@pytest.fixture()
def auth_headers(client, test_user):
    # Create a token payload directly (bypass /auth/login) and return Authorization header
    token = security_module.create_access_token({"user_id": int(test_user.customer_id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def kyc_unverified_user():
    db = SessionLocal()
    user = Customer(
        full_name="KYC User",
        email="kycuser@example.com",
        phone_number="+919876543210",
        password_hash=hash_password("Secret123"),
        kyc_status="PENDING"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

# Override get_current_user for endpoints that depend on it in tests when needed
def override_current_user_verified(test_user_fixture=None):
    def _override():
        return {"user_id": int(test_user_fixture.customer_id)}
    return _override

# Note: individual tests will set app.dependency_overrides[security_module.get_current_user] as needed
