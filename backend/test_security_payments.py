import importlib
import json
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def build_client(tmp_path):
    os.environ["HOROSCOPO_DB_PATH"] = str(tmp_path / "horoscopo-test.db")
    os.environ["DATA_REQUESTS_PATH"] = str(tmp_path / "data-requests.json")
    os.environ["APP_BASE_URL"] = "https://hypersecit.com.br"
    os.environ["PAYPAL_CLIENT_ID"] = "paypal-client"
    os.environ["PAYPAL_SECRET"] = "paypal-secret"
    os.environ["MP_ACCESS_TOKEN"] = "mp-token"
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_123"
    os.environ["STRIPE_PRICE_PREMIUM"] = "price_premium"
    os.environ["STRIPE_PRICE_VIP"] = "price_vip"
    os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    backend_dir = Path(__file__).resolve().parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    if "main" in sys.modules:
        del sys.modules["main"]

    main = importlib.import_module("main")
    return TestClient(main.app), main


def register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "nome": "User Seguro",
            "email": "seguro@example.com",
            "password": "senha-segura-123",
            "signo": "Aries",
        },
    )
    assert response.status_code == 200
    return response.json()


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_paypal_order_requires_auth_and_server_side_plan_price(tmp_path, monkeypatch):
    client, main = build_client(tmp_path)
    created_orders = []

    monkeypatch.setattr(main, "get_paypal_access_token", lambda: "paypal-token")

    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {"id": "PAYPAL_ORDER_1", "links": [{"rel": "approve", "href": "https://paypal.test/approve"}]}

    def fake_post(url, json=None, headers=None, timeout=None, **kwargs):
        created_orders.append(json)
        return FakeResp()

    monkeypatch.setattr(main.requests, "post", fake_post)

    unauthenticated = client.post(
        "/api/paypal/create-order",
        json={"plano": "vip", "amount": "0.01", "currency": "BRL"},
    )
    assert unauthenticated.status_code == 401
    assert created_orders == []

    user = register_user(client)
    response = client.post(
        "/api/paypal/create-order",
        json={"plano": "vip", "amount": "0.01", "currency": "BRL"},
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    assert created_orders[0]["purchase_units"][0]["amount"] == {"currency_code": "BRL", "value": "150.00"}
    assert created_orders[0]["purchase_units"][0]["custom_id"] == user["user"]["id"]
    assert created_orders[0]["purchase_units"][0]["reference_id"] == "vip"


def test_mercadopago_pix_requires_auth_and_server_side_plan_price(tmp_path, monkeypatch):
    client, main = build_client(tmp_path)
    created_payments = []

    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "pending",
                "id": 12345,
                "point_of_interaction": {
                    "transaction_data": {
                        "qr_code": "pix-code",
                        "qr_code_base64": "pix-base64",
                    }
                },
            }

    def fake_post(url, json=None, headers=None, timeout=None, **kwargs):
        created_payments.append(json)
        return FakeResp()

    monkeypatch.setattr(main.requests, "post", fake_post)

    unauthenticated = client.post(
        "/api/mercadopago/create-pix",
        json={"plano": "premium", "amount": "0.01"},
    )
    assert unauthenticated.status_code == 401
    assert created_payments == []

    user = register_user(client)
    response = client.post(
        "/api/mercadopago/create-pix",
        json={"plano": "premium", "amount": "0.01"},
        headers=auth_headers(user["access_token"]),
    )

    assert response.status_code == 200
    assert created_payments[0]["transaction_amount"] == 49.90
    assert created_payments[0]["external_reference"] == f"{user['user']['id']}:premium"


def test_authenticated_user_can_export_and_delete_own_data(tmp_path):
    client, _ = build_client(tmp_path)
    user = register_user(client)
    headers = auth_headers(user["access_token"])

    export_response = client.get("/api/me/export", headers=headers)
    assert export_response.status_code == 200
    exported = export_response.json()
    assert exported["user"]["email"] == "seguro@example.com"
    assert "password_hash" not in exported["user"]
    assert "access_token" not in exported["user"]

    delete_response = client.delete("/api/me", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"

    me_response = client.get("/api/me", headers=headers)
    assert me_response.status_code == 401

    audit_log = json.loads((tmp_path / "data-requests.json").read_text(encoding="utf-8"))
    deletion_event = audit_log[-1]
    assert deletion_event["tipo"] == "account_deletion_completed"
    assert deletion_event["email_hash"]
    assert "email" not in deletion_event


def test_api_responses_include_security_headers(tmp_path):
    client, _ = build_client(tmp_path)
    response = client.get("/api/metricas")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert response.headers["content-security-policy"] == (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    )
    assert response.headers["cache-control"] == "no-store"
