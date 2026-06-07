from pathlib import Path


FRONTEND_INDEX = Path(__file__).resolve().parents[1] / "frontend" / "index.html"


def test_frontend_handles_pix_ticket_url_and_expired_session_message():
    html = FRONTEND_INDEX.read_text(encoding="utf-8")

    assert "ticket_url" in html
    assert "Sessão expirada" in html


def test_frontend_auth_select_options_are_legible_and_login_error_is_actionable():
    html = FRONTEND_INDEX.read_text(encoding="utf-8")

    assert ".form-field option" in html
    assert "Conta não encontrada" in html


def test_frontend_uses_local_tailwind_bundle_for_store_builds():
    html = FRONTEND_INDEX.read_text(encoding="utf-8")

    assert "styles/tailwind.css" in html
    assert "cdn.tailwindcss.com" not in html


def test_frontend_store_build_blocks_external_payment_ui():
    html = FRONTEND_INDEX.read_text(encoding="utf-8")

    assert "const PUBLIC_APP_URL = 'https://seufuturo.blog.br'" in html
    assert "const isStoreBuild" in html
    assert "activePlanos" in html
    assert "if (!isStoreBuild && 'serviceWorker' in navigator)" in html
    assert "document.body.dataset.distribution = 'store'" in html
    assert "Compras de Premium e VIP ficam indisponiveis" in html


def test_frontend_checkout_exposes_only_paypal_and_pix():
    html = FRONTEND_INDEX.read_text(encoding="utf-8")

    assert "Pagar com PayPal" in html
    assert "Pagar com PIX" in html
    assert "confirmCheckoutBtn" not in html
    assert "Pagar com Cartão" not in html
    assert "Stripe" not in html
    assert "stripe" not in html
    assert "/api/checkout/session" not in html


def test_frontend_uses_brazilian_cancer_sign_label():
    html = FRONTEND_INDEX.read_text(encoding="utf-8")

    assert "Câncer" in html
    assert "<option value=\"Cancro\">Cancro</option>" not in html
    assert "Cancro" not in html
