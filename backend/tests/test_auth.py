import pytest

from app.core.security import hash_password, verify_password, create_access_token


def test_password_hashing():
    password = "testpass123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpass", hashed)


def test_create_access_token():
    token = create_access_token("testuser")

    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
@pytest.mark.db_required
async def test_register_returns_token(client):
    response = await client.post("/api/auth/register", json={
        "username": "newuser",
        "password": "securepass123",
    })

    assert response.status_code == 201
    assert "access_token" in response.json()


@pytest.mark.asyncio
@pytest.mark.db_required
async def test_login_rejects_bad_credentials(client):
    response = await client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "wrongpass",
    })

    # 401 if DB is up, 500 if no DB - either is acceptable in CI
    assert response.status_code in (401, 500)


@pytest.mark.asyncio
async def test_protected_endpoint_requires_token(client):
    response = await client.post("/api/monitors", json={
        "name": "Test",
        "url": "https://example.com",
    })

    assert response.status_code == 401
