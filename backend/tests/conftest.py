import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.services.auth_service import AuthService
from backend.app.schemas.auth import UserRegister

# Use a clean test sqlite database
TEST_DB_URL = "sqlite:///./test_fittrack.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_fittrack.db"):
        try:
            os.remove("./test_fittrack.db")
        except:
            pass


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_user(db_session):
    user_in = UserRegister(
        name="Test Athlete",
        email="athlete@test.com",
        password="securePassword123!",
    )
    user, token = AuthService.register_user(db_session, user_in)
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture
def other_user(db_session):
    user_in = UserRegister(
        name="Second Athlete",
        email="second@test.com",
        password="anotherPassword456!",
    )
    user, token = AuthService.register_user(db_session, user_in)
    return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}
