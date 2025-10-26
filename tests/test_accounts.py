import pytest
from app.routes import account_route


def test_create_account_success(client, test_user, auth_headers):
    # Ensure dependency override for current user returns our test_user id
    from app.core import security as security_module
    app = client.app
    app.dependency_overrides[security_module.get_current_user] = lambda: {"user_id": int(test_user.customer_id)}

    payload = {
        "account_type": "SAVINGS",
        "initial_deposit": 5000.00,
    }

    resp = client.post("/accounts/create", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["data"]["account_type"] == "SAVINGS"
    assert float(body["data"]["balance"]) == pytest.approx(5000.00)


def test_create_account_insufficient_deposit(client, test_user, auth_headers):
    from app.core import security as security_module
    app = client.app
    app.dependency_overrides[security_module.get_current_user] = lambda: {"user_id": int(test_user.customer_id)}

    payload = {
        "account_type": "SAVINGS",
        "initial_deposit": 100.00,

    }

    resp = client.post("/accounts/create", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "failed"
    assert "Minimum deposit" in body["msg"]


def test_create_account_invalid_type(client, test_user, auth_headers):
    from app.core import security as security_module
    app = client.app
    app.dependency_overrides[security_module.get_current_user] = lambda: {"user_id": int(test_user.customer_id)}

    payload = {
        "account_type": "LOAN",
        "initial_deposit": 10000.00,
    }

    resp = client.post("/accounts/create", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "failed"
    assert "Invalid account type" in body["msg"]


def test_create_account_duplicate(client, test_user, auth_headers):
    from app.core import security as security_module
    app = client.app
    app.dependency_overrides[security_module.get_current_user] = lambda: {"user_id": int(test_user.customer_id)}

    payload = {
        "account_type": "CURRENT",
        "initial_deposit": 1000.00,
    }

    # First creation should succeed
    r1 = client.post("/accounts/create", json=payload, headers=auth_headers)
    assert r1.status_code == 200
    assert r1.json()["status"] == "success"

    # Second creation of same account type should fail
    r2 = client.post("/accounts/create", json=payload, headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "failed"
    assert "already exists" in r2.json()["msg"]


def test_create_account_kyc_incomplete(client, kyc_unverified_user):
    from app.core import security as security_module
    app = client.app
    # token for the unverified user
    token = security_module.create_access_token({"user_id": int(kyc_unverified_user.customer_id), "email": kyc_unverified_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    app.dependency_overrides[security_module.get_current_user] = lambda: {"user_id": int(kyc_unverified_user.customer_id)}

    payload = {
        "account_type": "SAVINGS",
        "initial_deposit": 5000.00,
    }

    resp = client.post("/accounts/create", json=payload, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "failed"
    assert body["msg"] == "KYC not completed"
