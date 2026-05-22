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
