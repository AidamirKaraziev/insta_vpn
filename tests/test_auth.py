from conftest import client


def test_register():
    response = client.post("/auth/register", json={
        "email": "string",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "string",
        "role_id": 1
    })

    assert response.status_code == 201
