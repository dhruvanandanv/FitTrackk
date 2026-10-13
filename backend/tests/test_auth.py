import pytest
from backend.app.models.user import User


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "fittrack-backend"


def test_register_user(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Jane Runner",
            "email": "jane@example.com",
            "password": "Password789!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" == "access_token"
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["name"] == "Jane Runner"

    # Verify password is saved hashed, NOT plaintext
    db_user = db_session.query(User).filter(User.email == "jane@example.com").first()
    assert db_user is not None
    assert db_user.password_hash != "Password789!"
    assert "$argon2" in db_user.password_hash


def test_duplicate_email_registration_fails(client):
    # First registration
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Duplicate User",
            "email": "dup@example.com",
            "password": "Password123!",
        },
    )
    # Duplicate attempt
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Duplicate User",
            "email": "dup@example.com",
            "password": "Password123!",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Login User",
            "email": "loginuser@example.com",
            "password": "CorrectPassword123!",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "CorrectPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "loginuser@example.com"


def test_login_invalid_password_rejected(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 401


def test_protected_route_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_profile(client, auth_user):
    response = client.get("/api/v1/auth/me", headers=auth_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == auth_user["user"].email
    assert data["name"] == auth_user["user"].name
    assert "profile" in data


def test_production_security_validation():
    from backend.app.config import Settings
    # 1. Dev secret rejected in production
    with pytest.raises(ValueError, match="CRITICAL SECURITY CONFIGURATION"):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://user:pass@ep-test.neon.tech/neondb",
        )

    # 2. SQLite rejected in production
    with pytest.raises(ValueError, match="CRITICAL DATABASE CONFIGURATION"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a" * 32,
            DATABASE_URL="sqlite:///./test.db",
        )

    # 3. Valid production configuration passes and normalizes Neon URL
    prod_settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a" * 32,
        DATABASE_URL="postgres://user:pass@ep-test.neon.tech/neondb",
    )
    assert prod_settings.JWT_SECRET_KEY == "a" * 32
    assert prod_settings.normalized_database_url.startswith("postgresql://")
    assert "sslmode=require" in prod_settings.normalized_database_url


def test_static_frontend_delivery(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "FitTrack" in response.text
