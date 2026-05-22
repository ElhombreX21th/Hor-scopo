import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def build_client(tmp_path):
    os.environ["HOROSCOPO_DB_PATH"] = str(tmp_path / "horoscopo-test.db")
    os.environ["APP_BASE_URL"] = "https://hypersecit.com.br"
    os.environ["ADMIN_TOKEN"] = "admintoken123"
    os.environ.pop("VERCEL", None)
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("POSTGRES_URL", None)
    os.environ.pop("POSTGRES_URL_NON_POOLING", None)
    os.environ.pop("POSTGRES_PRISMA_URL", None)
    os.environ.pop("SUPABASE_DB_URL", None)
    backend_dir = Path(__file__).resolve().parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    if "main" in sys.modules:
        del sys.modules["main"]

    main = importlib.import_module("main")
    return TestClient(main.app)


def admin_headers():
    return {"Authorization": "Bearer admintoken123"}


def test_admin_refund_mercadopago_and_list(tmp_path, monkeypatch):
    client = build_client(tmp_path)

    # mock requests.post for mercadopago refund
    class FakeResp:
        def __init__(self, ok=True, json_data=None, text=''):
            self.ok = ok
            self._json = json_data or {"id": 999, "status": "refunded"}
            self.text = text

        def json(self):
            return self._json

    def fake_post(url, headers=None, json=None, timeout=None):
        return FakeResp()

    monkeypatch.setattr('requests.post', fake_post)

    res = client.post('/api/admin/refund', json={"provider": "mercadopago", "payment_id": "12345", "user_id": None}, headers=admin_headers())
    assert res.status_code == 200
    body = res.json()
    assert body.get('provider') == 'mercadopago'
    assert 'refund' in body

    # list requests
    list_res = client.get('/api/admin/requests', headers=admin_headers())
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)


def test_admin_refund_paypal_and_stripe_mock(tmp_path, monkeypatch):
    client = build_client(tmp_path)

    # mock get_paypal_access_token and requests.post for paypal
    import main as mainmod

    monkeypatch.setattr(mainmod, 'get_paypal_access_token', lambda: 'fake_paypal_token')

    class FakeRespPay:
        def __init__(self, ok=True):
            self.ok = ok

        def json(self):
            return {"id": "refund_paypal_1"}

        @property
        def text(self):
            return 'ok'

    def fake_post_paypal(url, headers=None, json=None, timeout=None):
        return FakeRespPay()

    monkeypatch.setattr('requests.post', fake_post_paypal)

    # PayPal refund
    res_pay = client.post('/api/admin/refund', json={"provider": "paypal", "payment_id": "cap_123", "user_id": None}, headers=admin_headers())
    assert res_pay.status_code == 200
    assert 'refund' in res_pay.json()

    # mock stripe
    class FakeStripe:
        class Refund:
            @staticmethod
            def create(charge=None):
                return {"id": "refund_stripe_1"}

    monkeypatch.setitem(sys.modules, 'stripe', FakeStripe)

    res_st = client.post('/api/admin/refund', json={"provider": "stripe", "payment_id": "ch_123", "user_id": None}, headers=admin_headers())
    assert res_st.status_code == 200
    assert 'refund' in res_st.json()
