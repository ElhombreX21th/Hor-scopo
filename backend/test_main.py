import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def build_client(tmp_path):
    os.environ["HOROSCOPO_DB_PATH"] = str(tmp_path / "horoscopo-test.db")
    os.environ["APP_BASE_URL"] = "https://seufuturo.blog.br"
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_123"
    os.environ["STRIPE_PRICE_PREMIUM"] = "price_premium"
    os.environ["STRIPE_PRICE_VIP"] = "price_vip"
    os.environ.pop("PAYPAL_CLIENT_ID", None)
    os.environ.pop("PAYPAL_SECRET", None)
    os.environ.pop("MP_ACCESS_TOKEN", None)
    os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    backend_dir = Path(__file__).resolve().parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    if "main" in sys.modules:
        del sys.modules["main"]

    main = importlib.import_module("main")
    return TestClient(main.app)


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_paid_plan_requires_authenticated_subscription(tmp_path):
    client = build_client(tmp_path)

    basic_response = client.get("/api/horoscopo", params={"signo": "Aries"})
    assert basic_response.status_code == 200
    assert "previsao_diaria" in basic_response.json()

    paid_response = client.get(
        "/api/horoscopo",
        params={"signo": "Aries", "plano": "vip"},
    )

    assert paid_response.status_code == 402
    assert paid_response.json()["detail"] == "Plano vip requer assinatura ativa."


def test_auth_validation_errors_are_human_readable(tmp_path):
    client = build_client(tmp_path)

    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin", "password": "senha-segura-123"},
    )
    assert login_response.status_code == 422
    assert login_response.json()["detail"] == "Email inválido."

    register_response = client.post(
        "/api/auth/register",
        json={"nome": "Admin", "email": "admin", "password": "senha-segura-123", "signo": "Aries"},
    )
    assert register_response.status_code == 422
    assert register_response.json()["detail"] == "Email inválido."


def test_payment_config_reports_available_public_providers(tmp_path):
    client = build_client(tmp_path)

    response = client.get("/api/payments/config")

    assert response.status_code == 200
    assert response.json() == {
        "stripe": True,
        "paypal": False,
        "pix": False,
    }


def test_register_checkout_webhook_unlocks_premium_content(tmp_path, monkeypatch):
    client = build_client(tmp_path)
    main = sys.modules["main"]

    def fake_customer(user):
        assert user["email"] == "ana@example.com"
        return "cus_ana"

    def fake_checkout_session(user, plano, price_id, customer_id):
        assert plano == "premium"
        assert price_id == "price_premium"
        assert customer_id == "cus_ana"
        return {
            "id": "cs_premium_123",
            "url": "https://checkout.stripe.com/c/pay/cs_premium_123",
        }

    monkeypatch.setattr(main, "get_or_create_stripe_customer", fake_customer)
    monkeypatch.setattr(main, "create_stripe_checkout_session", fake_checkout_session)

    register_response = client.post(
        "/api/auth/register",
        json={
            "nome": "Ana Cosmos",
            "email": "ana@example.com",
            "password": "senha-segura-123",
            "signo": "Touro",
        },
    )

    assert register_response.status_code == 200
    registered = register_response.json()
    assert registered["user"]["plano"] == "basic"
    token = registered["access_token"]

    blocked_response = client.get(
        "/api/horoscopo",
        params={"signo": "Touro", "plano": "premium"},
        headers=auth_headers(token),
    )
    assert blocked_response.status_code == 402

    session_response = client.post(
        "/api/checkout/session",
        json={"plano": "premium"},
        headers=auth_headers(token),
    )
    assert session_response.status_code == 200
    session = session_response.json()
    assert session["plano"] == "premium"
    assert session["status"] == "pending"
    assert session["checkout_url"] == "https://checkout.stripe.com/c/pay/cs_premium_123"

    still_blocked_response = client.get(
        "/api/horoscopo",
        params={"signo": "Touro", "plano": "premium"},
        headers=auth_headers(token),
    )
    assert still_blocked_response.status_code == 402

    webhook_response = client.post(
        "/api/stripe/webhook",
        json={
            "id": "evt_checkout_completed",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_premium_123",
                    "customer": "cus_ana",
                    "subscription": "sub_premium_123",
                    "client_reference_id": registered["user"]["id"],
                    "payment_status": "paid",
                    "metadata": {
                        "user_id": registered["user"]["id"],
                        "plano": "premium",
                    },
                }
            },
        },
    )
    assert webhook_response.status_code == 200
    assert client.get("/api/me", headers=auth_headers(token)).json()["user"]["plano"] == "premium"

    horoscope_response = client.get(
        "/api/horoscopo",
        params={"signo": "Touro", "plano": "premium"},
        headers=auth_headers(token),
    )

    assert horoscope_response.status_code == 200
    body = horoscope_response.json()
    assert body["plano_consultado"] == "premium"
    assert "amor" in body
    assert "carreira" in body
    assert "dados_da_sorte" not in body


def test_stripe_checkout_redirects_to_subscription_confirmation(tmp_path, monkeypatch):
    build_client(tmp_path)
    main = sys.modules["main"]
    created_session = {}

    def fake_create(**kwargs):
        created_session.update(kwargs)
        return {"id": "cs_redirect_123", "url": "https://checkout.stripe.com/c/pay/cs_redirect_123"}

    monkeypatch.setattr(main.stripe.checkout.Session, "create", fake_create)

    session = main.create_stripe_checkout_session(
        {"id": "user_123", "email": "cliente@example.com", "nome": "Cliente"},
        "premium",
        "price_premium",
        "cus_cliente",
    )

    assert session["id"] == "cs_redirect_123"
    assert created_session["success_url"] == (
        "https://seufuturo.blog.br/confirmacao-assinatura?checkout=success&session_id={CHECKOUT_SESSION_ID}"
    )
    assert created_session["cancel_url"] == "https://seufuturo.blog.br/?checkout=cancel"


def test_vip_webhook_unlocks_luck_and_mystic_advice(tmp_path, monkeypatch):
    client = build_client(tmp_path)
    main = sys.modules["main"]
    monkeypatch.setattr(main, "get_or_create_stripe_customer", lambda user: "cus_bruno")
    monkeypatch.setattr(
        main,
        "create_stripe_checkout_session",
        lambda user, plano, price_id, customer_id: {"id": "cs_vip_123", "url": "https://checkout.stripe.com/c/pay/cs_vip_123"},
    )

    register_response = client.post(
        "/api/auth/register",
        json={
            "nome": "Bruno Lunar",
            "email": "bruno@example.com",
            "password": "senha-segura-123",
            "signo": "Peixes",
        },
    )
    token = register_response.json()["access_token"]
    user_id = register_response.json()["user"]["id"]

    client.post(
        "/api/checkout/session",
        json={"plano": "vip"},
        headers=auth_headers(token),
    )
    client.post(
        "/api/stripe/webhook",
        json={
            "id": "evt_vip_completed",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_vip_123",
                    "customer": "cus_bruno",
                    "subscription": "sub_vip_123",
                    "payment_status": "paid",
                    "metadata": {"user_id": user_id, "plano": "vip"},
                }
            },
        },
    )

    horoscope_response = client.get(
        "/api/horoscopo",
        params={"signo": "Peixes", "plano": "vip"},
        headers=auth_headers(token),
    )

    assert horoscope_response.status_code == 200
    body = horoscope_response.json()
    assert body["plano_consultado"] == "vip"
    assert "dados_da_sorte" in body
    assert "conselho_mistico_vip" in body


def test_subscription_deleted_webhook_downgrades_to_basic(tmp_path, monkeypatch):
    client = build_client(tmp_path)
    main = sys.modules["main"]
    monkeypatch.setattr(main, "get_or_create_stripe_customer", lambda user: "cus_cancel")
    monkeypatch.setattr(
        main,
        "create_stripe_checkout_session",
        lambda user, plano, price_id, customer_id: {"id": "cs_cancel_123", "url": "https://checkout.stripe.com/c/pay/cs_cancel_123"},
    )

    registered = client.post(
        "/api/auth/register",
        json={
            "nome": "Clara Portal",
            "email": "clara@example.com",
            "password": "senha-segura-123",
            "signo": "Libra",
        },
    ).json()
    token = registered["access_token"]

    client.post("/api/checkout/session", json={"plano": "vip"}, headers=auth_headers(token))
    client.post(
        "/api/stripe/webhook",
        json={
            "id": "evt_cancel_checkout",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_cancel_123",
                    "customer": "cus_cancel",
                    "subscription": "sub_cancel_123",
                    "payment_status": "paid",
                    "metadata": {"user_id": registered["user"]["id"], "plano": "vip"},
                }
            },
        },
    )

    assert client.get("/api/me", headers=auth_headers(token)).json()["user"]["plano"] == "vip"

    deleted_response = client.post(
        "/api/stripe/webhook",
        json={
            "id": "evt_subscription_deleted",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_cancel_123",
                    "customer": "cus_cancel",
                    "status": "canceled",
                }
            },
        },
    )

    assert deleted_response.status_code == 200
    assert client.get("/api/me", headers=auth_headers(token)).json()["user"]["plano"] == "basic"


def test_billing_portal_uses_stripe_customer(tmp_path, monkeypatch):
    client = build_client(tmp_path)
    main = sys.modules["main"]
    monkeypatch.setattr(main, "get_or_create_stripe_customer", lambda user: "cus_portal")
    monkeypatch.setattr(
        main,
        "create_stripe_checkout_session",
        lambda user, plano, price_id, customer_id: {"id": "cs_portal_123", "url": "https://checkout.stripe.com/c/pay/cs_portal_123"},
    )
    monkeypatch.setattr(
        main,
        "create_stripe_portal_session",
        lambda customer_id: {"url": f"https://billing.stripe.com/p/session/{customer_id}"},
    )

    registered = client.post(
        "/api/auth/register",
        json={
            "nome": "Dora Portal",
            "email": "dora@example.com",
            "password": "senha-segura-123",
            "signo": "Virgem",
        },
    ).json()
    token = registered["access_token"]

    client.post("/api/checkout/session", json={"plano": "premium"}, headers=auth_headers(token))
    portal_response = client.post("/api/billing/portal", headers=auth_headers(token))

    assert portal_response.status_code == 200
    assert portal_response.json()["portal_url"] == "https://billing.stripe.com/p/session/cus_portal"


def test_accented_and_portuguese_sign_names_use_specific_predictions(tmp_path):
    client = build_client(tmp_path)

    gemeos_response = client.get("/api/horoscopo", params={"signo": "Gémeos"})
    cancro_response = client.get("/api/horoscopo", params={"signo": "Cancro"})

    assert gemeos_response.status_code == 200
    assert cancro_response.status_code == 200
    assert gemeos_response.json()["previsao_diaria"].startswith("Comunicação")
    assert cancro_response.json()["previsao_diaria"].startswith("Emoções")
