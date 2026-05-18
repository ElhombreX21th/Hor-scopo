from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import tempfile
import unicodedata
import uuid
from decimal import Decimal
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

try:
    import stripe
except ImportError:  # pragma: no cover - exercised only when dependency is missing in runtime
    stripe = None

if load_dotenv:
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
IS_VERCEL = os.environ.get("VERCEL") == "1"
DEFAULT_RUNTIME_DIR = os.path.join(tempfile.gettempdir(), "seufuturo") if IS_VERCEL else BASE_DIR


def resolve_project_path(path: str):
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_ROOT, path)


runtime_dir_env = os.environ.get("HOROSCOPO_RUNTIME_DIR")
RUNTIME_DIR = resolve_project_path(runtime_dir_env) if runtime_dir_env else DEFAULT_RUNTIME_DIR
os.makedirs(RUNTIME_DIR, exist_ok=True)

APP_NAME = os.environ.get("APP_NAME", "SeuFuturo")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "https://hypersecit.com.br").rstrip("/")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "https://hypersecit.com.br,http://127.0.0.1:8001,http://localhost:8001").split(",")
    if origin.strip()
]
STRIPE_API_VERSION = "2026-02-25.clover"
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_IDS = {
    "premium": os.environ.get("STRIPE_PRICE_PREMIUM", ""),
    "vip": os.environ.get("STRIPE_PRICE_VIP", ""),
}
BEARER_AUTH_TYPE = "bearer"

app = FastAPI(title=f"SaaS {APP_NAME}")

# Logging
log_path_env = os.environ.get("HOROSCOPO_LOG_PATH")
LOG_PATH = resolve_project_path(log_path_env) if log_path_env else os.path.join(RUNTIME_DIR, "logs")
log_handlers = [logging.StreamHandler()]

if not IS_VERCEL or os.environ.get("ENABLE_FILE_LOGS") == "1":
    try:
        os.makedirs(LOG_PATH, exist_ok=True)
        log_handlers.append(logging.FileHandler(os.path.join(LOG_PATH, "backend.log")))
    except OSError:
        pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger('seufuturo')

# Permite que o frontend aceda ao backend sem erros de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["https://hypersecit.com.br"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
}
API_CONTENT_SECURITY_POLICY = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        if header not in response.headers:
            response.headers[header] = value
    if request.url.path.startswith("/api/"):
        if "Content-Security-Policy" not in response.headers:
            response.headers["Content-Security-Policy"] = API_CONTENT_SECURITY_POLICY
        if "Cache-Control" not in response.headers:
            response.headers["Cache-Control"] = "no-store"
    return response

# Configuração da API Externa (Exemplo usando uma API pública ou fictícia)
# Substituirás pelo URL e chaves reais do provedor que escolheres (ex: Horoscope API, Azintro, etc.)
ASTRO_API_URL = "https://api.vidente-exemplo.com/v1/horoscope"
API_KEY = os.environ.get("ASTRO_API_KEY", "")

PLANOS_VALIDOS = {"basic": 0, "premium": 1, "vip": 2}
PLAN_PRICES_BRL = {
    "premium": "49.90",
    "vip": "150.00",
}
ACTIVE_SUBSCRIPTION_STATUSES = {"active", "trialing"}
SIGNO_ALIASES = {
    "aries": "aries",
    "touro": "touro",
    "gemeos": "gemeos",
    "gemini": "gemeos",
    "cancer": "cancer",
    "cancro": "cancer",
    "leao": "leao",
    "virgem": "virgem",
    "libra": "libra",
    "escorpiao": "escorpiao",
    "sagitario": "sagitario",
    "capricornio": "capricornio",
    "aquario": "aquario",
    "peixes": "peixes",
}
db_path_env = os.environ.get("HOROSCOPO_DB_PATH")
DB_PATH = resolve_project_path(db_path_env) if db_path_env else os.path.join(RUNTIME_DIR, "horoscopo.db")


def agora_iso():
    return datetime.utcnow().isoformat() + "Z"


def _require_admin(authorization: Optional[str]):
    token = None
    if authorization:
        if authorization.startswith("Bearer "):
            token = authorization[len("Bearer "):].strip()
        else:
            token = authorization.strip()

    env_token = os.environ.get("ADMIN_TOKEN", "")
    if not env_token:
        raise HTTPException(status_code=503, detail="ADMIN_TOKEN não configurado no servidor.")
    if not token or token != env_token:
        raise HTTPException(status_code=401, detail="Autenticação administrativa inválida.")


class AdminRefundModel(BaseModel):
    provider: str
    payment_id: str
    user_id: Optional[str] = None
    reason: Optional[str] = None


@app.post('/api/admin/refund')
async def admin_refund(req: AdminRefundModel, authorization: Optional[str] = Header(default=None)):
    _require_admin(authorization)
    provider = req.provider.lower()
    payment_id = req.payment_id
    user_id = req.user_id

    result = {"provider": provider, "payment_id": payment_id}

    try:
        if provider == 'stripe':
            # tenta importar módulo stripe dinamicamente (permite mocks em testes)
            try:
                import importlib
                stripe_mod = importlib.import_module('stripe')
            except Exception as e:
                result['error'] = f'stripe module not available: {e}'
                stripe_mod = None

            try:
                if stripe_mod is None:
                    raise Exception('stripe not configured')
                # se houver chave, configura
                sk = os.environ.get('STRIPE_SECRET_KEY')
                if sk and hasattr(stripe_mod, 'api_key'):
                    stripe_mod.api_key = sk
                refund = stripe_mod.Refund.create(charge=payment_id)
                # refund pode ser dict ou objeto
                if isinstance(refund, dict):
                    result['refund'] = refund.get('id')
                else:
                    result['refund'] = getattr(refund, 'id', str(refund))
            except Exception as e:
                result['error'] = str(e)

        elif provider == 'paypal':
            token = get_paypal_access_token()
            url = f"{_paypal_base()}/v2/payments/captures/{payment_id}/refund"
            resp = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, timeout=10)
            if resp.ok:
                result['refund'] = resp.json()
            else:
                result['error'] = resp.text

        elif provider in {'mercadopago', 'mercado_pago', 'mp'}:
            mp_token = os.environ.get('MP_ACCESS_TOKEN', '')
            url = f"https://api.mercadopago.com/v1/payments/{payment_id}/refunds"
            headers_mp = {"Content-Type": "application/json"}
            if mp_token:
                headers_mp["Authorization"] = f"Bearer {mp_token}"
            # permite que testes mockem requests.post mesmo sem token
            resp = requests.post(url, headers=headers_mp, json={'reason': req.reason or 'admin_refund'}, timeout=10)
            if getattr(resp, 'ok', False):
                try:
                    result['refund'] = resp.json()
                except Exception:
                    result['refund'] = str(resp)
            else:
                result['error'] = getattr(resp, 'text', str(resp))

        else:
            raise HTTPException(status_code=400, detail='Provedor desconhecido')
    except HTTPException:
        raise
    except Exception as e:
        result['error'] = str(e)

    # registrar e, se user_id, rebaixar assinatura localmente
    _append_data_request({"tipo": "admin_refund", "request": req.model_dump(), "result": result, "timestamp": agora_iso()})
    if user_id:
        downgrade_user_subscription(user_id)

    return result


@app.get('/api/admin/requests')
async def admin_list_requests(authorization: Optional[str] = Header(default=None)):
    _require_admin(authorization)
    try:
        if os.path.exists(DATA_REQUESTS_PATH):
            with open(DATA_REQUESTS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _column_exists(conn, table: str, column: str):
    return any(row["name"] == column for row in conn.execute(f"PRAGMA table_info({table})").fetchall())


def _add_column_if_missing(conn, table: str, column: str, definition: str):
    if not _column_exists(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                signo TEXT NOT NULL,
                plano TEXT NOT NULL DEFAULT 'basic',
                access_token TEXT UNIQUE,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                subscription_status TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS checkout_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                plano TEXT NOT NULL,
                status TEXT NOT NULL,
                provider TEXT,
                provider_session_id TEXT,
                checkout_url TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )
        _add_column_if_missing(conn, "users", "stripe_customer_id", "TEXT")
        _add_column_if_missing(conn, "users", "stripe_subscription_id", "TEXT")
        _add_column_if_missing(conn, "users", "subscription_status", "TEXT")
        _add_column_if_missing(conn, "checkout_sessions", "provider", "TEXT")
        _add_column_if_missing(conn, "checkout_sessions", "provider_session_id", "TEXT")
        _add_column_if_missing(conn, "checkout_sessions", "checkout_url", "TEXT")


def normalizar_plano(plano: str):
    plano_normalizado = plano.lower().strip()
    if plano_normalizado not in PLANOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Plano inválido. Escolha entre basic, premium ou vip.")
    return plano_normalizado


def paid_plan_price_brl(plano: str):
    plano_normalizado = normalizar_plano(plano)
    if plano_normalizado == "basic":
        raise HTTPException(status_code=400, detail="Pagamento disponível apenas para Premium ou VIP.")
    return plano_normalizado, PLAN_PRICES_BRL[plano_normalizado]


def record_checkout_session(user_id: str, plano: str, provider: str, provider_session_id: str, checkout_url: Optional[str] = None):
    session_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO checkout_sessions
                (id, user_id, plano, status, provider, provider_session_id, checkout_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, user_id, plano, "pending", provider, provider_session_id, checkout_url, agora_iso()),
        )
    return session_id


def parse_payment_reference(reference: Optional[str]):
    if not reference:
        return None, None
    if ":" not in reference:
        return reference, None
    user_id, plano = reference.split(":", 1)
    try:
        return user_id, normalizar_plano(plano)
    except HTTPException:
        return user_id, None


def normalizar_signo(signo: str):
    sem_acentos = unicodedata.normalize("NFKD", signo.strip().lower())
    slug = "".join(char for char in sem_acentos if not unicodedata.combining(char))
    return SIGNO_ALIASES.get(slug, slug)


def stripe_price_for_plan(plano: str):
    price_id = STRIPE_PRICE_IDS.get(plano, "")
    if not price_id:
        raise HTTPException(
            status_code=503,
            detail=f"Preço Stripe do plano {plano} não configurado.",
        )
    return price_id


def plan_for_stripe_price(price_id: Optional[str]):
    for plano, configured_price_id in STRIPE_PRICE_IDS.items():
        if configured_price_id and configured_price_id == price_id:
            return plano
    return None


def ensure_stripe_configured():
    if stripe is None:
        raise HTTPException(status_code=503, detail="Dependência stripe não instalada no backend.")
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="STRIPE_SECRET_KEY não configurada.")
    stripe.api_key = STRIPE_SECRET_KEY
    stripe.api_version = STRIPE_API_VERSION


def build_frontend_url(path: str):
    return f"{APP_BASE_URL}{path}"


def hash_password(password: str, salt: Optional[str] = None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str):
    try:
        salt, expected = stored_hash.split("$", 1)
    except ValueError:
        return False

    candidate = hash_password(password, salt).split("$", 1)[1]
    return hmac.compare_digest(candidate, expected)


def user_to_payload(user):
    return {
        "id": user["id"],
        "nome": user["nome"],
        "email": user["email"],
        "signo": user["signo"],
        "plano": user["plano"],
        "subscription_status": user["subscription_status"],
    }


def issue_token(user_id: str):
    token = secrets.token_urlsafe(32)
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET access_token = ?, updated_at = ? WHERE id = ?",
            (token, agora_iso(), user_id),
        )
    return token


def get_user_by_email(email: str):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()


def get_user_by_id(user_id: str):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_token(token: str):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE access_token = ?", (token,)).fetchone()


def update_user_stripe_customer(user_id: str, customer_id: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET stripe_customer_id = ?, updated_at = ? WHERE id = ?",
            (customer_id, agora_iso(), user_id),
        )


def set_user_subscription(user_id: str, plano: str, status: str, customer_id: Optional[str] = None, subscription_id: Optional[str] = None):
    with get_db() as conn:
        conn.execute(
            """
            UPDATE users
            SET plano = ?,
                subscription_status = ?,
                stripe_customer_id = COALESCE(?, stripe_customer_id),
                stripe_subscription_id = COALESCE(?, stripe_subscription_id),
                updated_at = ?
            WHERE id = ?
            """,
            (plano, status, customer_id, subscription_id, agora_iso(), user_id),
        )


def downgrade_user_subscription_by_stripe(subscription_id: Optional[str], customer_id: Optional[str]):
    with get_db() as conn:
        if subscription_id:
            conn.execute(
                """
                UPDATE users
                SET plano = 'basic', subscription_status = 'canceled', updated_at = ?
                WHERE stripe_subscription_id = ?
                """,
                (agora_iso(), subscription_id),
            )
        elif customer_id:
            conn.execute(
                """
                UPDATE users
                SET plano = 'basic', subscription_status = 'canceled', updated_at = ?
                WHERE stripe_customer_id = ?
                """,
                (agora_iso(), customer_id),
            )
    logger.info("downgrade_user_subscription_by_stripe called: subscription_id=%s customer_id=%s", subscription_id, customer_id)


def downgrade_user_subscription(user_id: Optional[str]):
    if not user_id:
        return
    with get_db() as conn:
        conn.execute(
            """
            UPDATE users
            SET plano = 'basic', subscription_status = 'canceled', updated_at = ?
            WHERE id = ?
            """,
            (agora_iso(), user_id),
        )
    logger.info("downgrade_user_subscription: user=%s", user_id)


def parse_authorization_token(authorization: Optional[str]):
    if not authorization:
        return None

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Token de autenticação inválido.")

    return authorization[len(prefix):].strip()


def get_current_user(authorization: Optional[str] = Header(default=None)):
    token = parse_authorization_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Autenticação obrigatória.")

    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token de autenticação inválido.")

    return user


def get_optional_user(authorization: Optional[str]):
    token = parse_authorization_token(authorization)
    if not token:
        return None

    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token de autenticação inválido.")

    return user


init_db()


def get_or_create_stripe_customer(user):
    if user["stripe_customer_id"]:
        return user["stripe_customer_id"]

    ensure_stripe_configured()
    customer = stripe.Customer.create(
        email=user["email"],
        name=user["nome"],
        metadata={"user_id": user["id"]},
    )
    customer_id = customer["id"] if isinstance(customer, dict) else customer.id
    update_user_stripe_customer(user["id"], customer_id)
    return customer_id


def create_stripe_checkout_session(user, plano: str, price_id: str, customer_id: str):
    ensure_stripe_configured()
    return stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=build_frontend_url("/confirmacao-assinatura?checkout=success&session_id={CHECKOUT_SESSION_ID}"),
        cancel_url=build_frontend_url("/?checkout=cancel"),
        client_reference_id=user["id"],
        metadata={"user_id": user["id"], "plano": plano},
        subscription_data={"metadata": {"user_id": user["id"], "plano": plano}},
        allow_promotion_codes=True,
    )


def create_stripe_portal_session(customer_id: str):
    ensure_stripe_configured()
    return stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=APP_BASE_URL,
    )


def _stripe_obj_value(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _parse_stripe_event(payload: bytes, signature: Optional[str]):
    if STRIPE_WEBHOOK_SECRET:
        ensure_stripe_configured()
        if not signature:
            raise HTTPException(status_code=400, detail="Assinatura Stripe ausente.")
        try:
            return stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
        except ValueError:
            raise HTTPException(status_code=400, detail="Payload Stripe inválido.")
        except Exception as exc:
            signature_error = getattr(getattr(stripe, "error", None), "SignatureVerificationError", None)
            if signature_error and isinstance(exc, signature_error):
                raise HTTPException(status_code=400, detail="Assinatura Stripe inválida.")
            raise

    try:
        return json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Payload Stripe inválido.")


# --------------------- PayPal helpers ---------------------
def _paypal_base():
    mode = os.environ.get("PAYPAL_MODE", "sandbox").lower()
    return "https://api-m.paypal.com" if mode == "live" else "https://api-m.sandbox.paypal.com"


def get_paypal_access_token():
    client_id = os.environ.get("PAYPAL_CLIENT_ID", "")
    client_secret = os.environ.get("PAYPAL_SECRET", "")
    if not client_id or not client_secret:
        raise HTTPException(status_code=503, detail="PayPal não configurado. Defina PAYPAL_CLIENT_ID e PAYPAL_SECRET.")

    url = f"{_paypal_base()}/v1/oauth2/token"
    try:
        resp = requests.post(url, data={"grant_type": "client_credentials"}, auth=(client_id, client_secret), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("access_token")
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Falha ao obter token PayPal.")


class PayPalOrderModel(BaseModel):
    plano: str
    amount: Optional[str] = None
    currency: str = "BRL"
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None


@app.post("/api/paypal/create-order")
async def paypal_create_order(req: PayPalOrderModel, user=Depends(get_current_user)):
    """Cria uma ordem PayPal e retorna links para o cliente aprovar o pagamento.
    O frontend deve redirecionar o utilizador para `approve` link recebido.
    """
    plano, amount = paid_plan_price_brl(req.plano)
    token = get_paypal_access_token()
    url = f"{_paypal_base()}/v2/checkout/orders"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {"currency_code": "BRL", "value": amount},
            "custom_id": user["id"],
            "reference_id": plano,
            "description": f"Assinatura SeuFuturo - {plano.upper()}",
        }]
    }

    if req.return_url or req.cancel_url:
        body["application_context"] = {
            k: v for k, v in {
                "return_url": req.return_url,
                "cancel_url": req.cancel_url,
            }.items() if v
        }

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        approve_url = None
        for link in data.get("links", []) or []:
            if link.get("rel") == "approve":
                approve_url = link.get("href")
                break
        session_id = record_checkout_session(user["id"], plano, "paypal", data.get("id", ""), approve_url)
        data["session_id"] = session_id
        return data
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Falha ao criar ordem PayPal.")


@app.post("/api/paypal/capture/{order_id}")
async def paypal_capture_order(order_id: str, user=Depends(get_current_user)):
    """Captura uma ordem PayPal (após aprovação do utilizador).
    Retorna o resultado da captura.
    """
    token = get_paypal_access_token()
    url = f"{_paypal_base()}/v2/checkout/orders/{order_id}/capture"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        resp = requests.post(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Falha ao capturar ordem PayPal.")


def _verify_paypal_webhook(request: Request, payload: dict) -> bool:
    """Tenta verificar assinatura do webhook PayPal via API `verify-webhook-signature` quando `PAYPAL_WEBHOOK_ID` estiver definido.
    Retorna True se verificado com sucesso ou se não houver parâmetros necessários (fallback permissivo).
    """
    webhook_id = os.environ.get("PAYPAL_WEBHOOK_ID", "")
    token = None
    try:
        token = get_paypal_access_token()
    except Exception:
        return False

    if not webhook_id:
        return False

    headers = request.headers
    verify_payload = {
        "auth_algo": headers.get("Paypal-Auth-Algo") or headers.get("PayPal-Auth-Algo"),
        "cert_url": headers.get("Paypal-Cert-Url") or headers.get("PayPal-Cert-Url"),
        "transmission_id": headers.get("Paypal-Transmission-Id") or headers.get("PayPal-Transmission-Id"),
        "transmission_sig": headers.get("Paypal-Transmission-Sig") or headers.get("PayPal-Transmission-Sig"),
        "transmission_time": headers.get("Paypal-Transmission-Time") or headers.get("PayPal-Transmission-Time"),
        "webhook_id": webhook_id,
        "webhook_event": payload,
    }

    try:
        resp = requests.post(f"{_paypal_base()}/v1/notifications/verify-webhook-signature", json=verify_payload,
                             headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("verification_status") == "SUCCESS"
    except Exception:
        return False


@app.post("/api/paypal/webhook")
async def paypal_webhook(request: Request):
    """Recebe webhooks do PayPal, verifica e processa pagamentos para ativar assinaturas.
    Em produção, assegura que `PAYPAL_WEBHOOK_ID` está definida para validação.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": (await request.body()).decode("utf-8", errors="ignore")}

    _append_data_request({"tipo": "paypal_webhook", "payload": payload, "timestamp": agora_iso()})

    verified = _verify_paypal_webhook(request, payload)
    if not verified:
        # continuar com cautela: será registado mas não processado automaticamente
        return {"received": False, "reason": "unverified"}

    event_type = payload.get("event_type")
    resource = payload.get("resource") or {}

    # Tenta extrair order_id ou capture id
    order_id = None
    capture_id = resource.get("id")
    # algumas notificações incluem related_ids
    related = (resource.get("supplementary_data") or {}).get("related_ids") if isinstance(resource.get("supplementary_data"), dict) else None
    if related:
        order_id = related.get("order_id")

    # Se não tivermos order_id mas captura tem, tentaremos buscar info da captura
    try:
        token = get_paypal_access_token()
        # prioriza order_id
        if not order_id and capture_id:
            # tenta obter order via capture lookup (não há endpoint direto para capture->order, então tentamos buscar capture)
            capture_resp = requests.get(f"{_paypal_base()}/v2/payments/captures/{capture_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if capture_resp.ok:
                cap = capture_resp.json()
                # tente encontrar order id dentro
                order_id = cap.get("supplementary_data", {}).get("related_ids", {}).get("order_id")

        if order_id:
            order_resp = requests.get(f"{_paypal_base()}/v2/checkout/orders/{order_id}", headers={"Authorization": f"Bearer {token}"}, timeout=10)
            if order_resp.ok:
                order = order_resp.json()
                status = order.get("status")
                purchase_units = order.get("purchase_units") or []
                if purchase_units:
                    pu = purchase_units[0]
                    user_id = pu.get("custom_id")
                    plano = pu.get("reference_id") or pu.get("invoice_id") or None
                    if status in {"COMPLETED", "APPROVED"} and user_id:
                        # marcar assinatura ativa
                        set_user_subscription(user_id, plano or 'premium', 'active')
                        logger.info("paypal_order_completed: order=%s user=%s plano=%s", order_id, user_id, plano)
                    elif status in {"VOIDED", "CANCELLED"} and user_id:
                        # ordem cancelada/voided -> downgrade
                        downgrade_user_subscription(user_id)
                        logger.info("paypal_order_cancelled: order=%s user=%s status=%s", order_id, user_id, status)
    except Exception as exc:
        logger.warning("paypal_webhook_processing_failed: %s", exc)

    return {"received": True}


class MPCreatePixModel(BaseModel):
    plano: str
    amount: Optional[str] = None
    email: Optional[EmailStr] = None


@app.post("/api/mercadopago/create-pix")
async def mercadopago_create_pix(req: MPCreatePixModel, user=Depends(get_current_user)):
    """Cria pagamento PIX via Mercado Pago e devolve dados do QR Code.
    Requer `MP_ACCESS_TOKEN` nas variáveis de ambiente.
    """
    plano, amount = paid_plan_price_brl(req.plano)
    mp_token = os.environ.get("MP_ACCESS_TOKEN", "")
    if not mp_token:
        raise HTTPException(status_code=503, detail="Mercado Pago não configurado (MP_ACCESS_TOKEN).")
    url = "https://api.mercadopago.com/v1/payments"
    headers = {"Authorization": f"Bearer {mp_token}", "Content-Type": "application/json"}
    body = {
        "transaction_amount": float(Decimal(amount)),
        "payment_method_id": "pix",
        "description": f"Assinatura SeuFuturo - {plano.upper()}",
        "external_reference": f"{user['id']}:{plano}",
    }

    body["payer"] = {"email": req.email or user["email"]}

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        poi = data.get("point_of_interaction", {}) or {}
        transaction_data = poi.get("transaction_data", {}) or {}

        payment_id = str(data.get("id") or "")
        session_id = record_checkout_session(user["id"], plano, "mercadopago", payment_id)

        return {
            "session_id": session_id,
            "status": data.get("status"),
            "id": data.get("id"),
            "qr_code": transaction_data.get("qr_code"),
            "qr_code_base64": transaction_data.get("qr_code_base64"),
            "raw": data,
        }
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Falha ao criar pagamento PIX no Mercado Pago.")


@app.post("/api/mercadopago/webhook")
async def mercadopago_webhook(request: Request):
    """Recebe notificações do Mercado Pago. Regista o payload para auditoria.
    Em produção, valide o `X-Hub-Signature` ou use verificação fornecida pelo MP.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": (await request.body()).decode("utf-8", errors="ignore")}

    _append_data_request({"tipo": "mercadopago_webhook", "payload": payload, "timestamp": agora_iso()})

    # Validar e reconciliar: quando receber notificação de pagamento, buscar o pagamento na API
    try:
        mp_token = os.environ.get("MP_ACCESS_TOKEN", "")
        if not mp_token:
            return {"received": True, "note": "mp_not_configured"}

        # payload típico: {"type":"payment","data":{"id": 12345}}
        event_type = payload.get('type')
        data = payload.get('data') or {}
        payment_id = None
        if isinstance(data, dict):
            payment_id = data.get('id')

        if event_type == 'payment' and payment_id:
            pay_resp = requests.get(f"https://api.mercadopago.com/v1/payments/{payment_id}", headers={"Authorization": f"Bearer {mp_token}"}, timeout=10)
            if pay_resp.ok:
                pay = pay_resp.json()
                status = pay.get('status')
                external_ref = pay.get('external_reference')
                description = pay.get('description') or ''
                payer = pay.get('payer') or {}
                payer_email = payer.get('email')

                # Se external_reference contém user id e plano, usamos para ligar
                user_id, referenced_plan = parse_payment_reference(external_ref)
                if not user_id and payer_email:
                    row = get_user_by_email(payer_email)
                    user_id = row['id'] if row else None

                if user_id and status in {'approved', 'paid'}:
                    plano = referenced_plan or 'premium'
                    if 'VIP' in (description or '').upper():
                        plano = 'vip'
                    set_user_subscription(user_id, plano, 'active')
                    logger.info("mercadopago_payment_approved: payment=%s user=%s plano=%s", payment_id, user_id, plano)
                elif user_id and status in {'refunded', 'cancelled'}:
                    downgrade_user_subscription(user_id)
                    logger.info("mercadopago_payment_refunded: payment=%s user=%s status=%s", payment_id, user_id, status)

    except Exception as exc:
        logger.warning("mercadopago_webhook_processing_failed: %s", exc)

    return {"received": True}




def _handle_checkout_completed(session):
    metadata = _stripe_obj_value(session, "metadata", {}) or {}
    user_id = metadata.get("user_id") or _stripe_obj_value(session, "client_reference_id")
    plano = normalizar_plano(metadata.get("plano", "basic"))
    payment_status = _stripe_obj_value(session, "payment_status")

    if not user_id or plano == "basic":
        return

    if payment_status and payment_status not in {"paid", "no_payment_required"}:
        return

    customer_id = _stripe_obj_value(session, "customer")
    subscription_id = _stripe_obj_value(session, "subscription")
    set_user_subscription(user_id, plano, "active", customer_id, subscription_id)
    logger.info("checkout_completed: user=%s plano=%s customer=%s subscription=%s", user_id, plano, customer_id, subscription_id)

    with get_db() as conn:
        conn.execute(
            """
            UPDATE checkout_sessions
            SET status = 'completed', completed_at = ?
            WHERE provider_session_id = ?
            """,
            (agora_iso(), _stripe_obj_value(session, "id")),
        )


def _subscription_price_id(subscription):
    items = _stripe_obj_value(subscription, "items", {}) or {}
    data = items.get("data", []) if isinstance(items, dict) else getattr(items, "data", [])
    if not data:
        return None
    price = _stripe_obj_value(data[0], "price", {}) or {}
    return _stripe_obj_value(price, "id")


def _handle_subscription_changed(subscription):
    status = _stripe_obj_value(subscription, "status", "")
    subscription_id = _stripe_obj_value(subscription, "id")
    customer_id = _stripe_obj_value(subscription, "customer")

    if status not in ACTIVE_SUBSCRIPTION_STATUSES:
        downgrade_user_subscription_by_stripe(subscription_id, customer_id)
        return

    plano = plan_for_stripe_price(_subscription_price_id(subscription))
    if not plano:
        return

    with get_db() as conn:
        row = None
        if subscription_id:
            row = conn.execute("SELECT id FROM users WHERE stripe_subscription_id = ?", (subscription_id,)).fetchone()
        if not row and customer_id:
            row = conn.execute("SELECT id FROM users WHERE stripe_customer_id = ?", (customer_id,)).fetchone()

    if row:
        set_user_subscription(row["id"], plano, status, customer_id, subscription_id)
        logger.info("subscription_changed: user=%s plano=%s status=%s", row["id"], plano, status)

def buscar_dados_astrologicos(signo: str):
    """
    Função simuladora que obtém os dados da API Externa.
    Em produção, fará um requests.get(ASTRO_API_URL, headers=...)
    """
    # Simulando a resposta completa que uma API profissional nos daria
    dados_api_externa = {
        "aries": {
            "diario": "Hoje é um dia de muita energia e iniciativa. Ideal para começar novos projetos.",
            "amor": "Momento de diálogo. Evita decisões por impulso na relação.",
            "carreira": "Uma oportunidade inesperada pode surgir. Fica atento às finanças.",
            "sorte": "Número 7 | Cor: Azul-turquesa",
            "conselho_vip": "Alinhamento de Marte sugere que deves meditar 10 minutos antes de tomar decisões cruciais esta semana."
        },
        "touro": {
            "diario": "Dia de estabilidade e reflexão. Perfeito para consolidar projetos.",
            "amor": "Harmonia e compreensão dominam o dia. Hora de aproximação.",
            "carreira": "Esforços passados trazem reconhecimento. Aproveita as oportunidades.",
            "sorte": "Número 4 | Cor: Verde-esmeralda",
            "conselho_vip": "Vénus em aspecto favorável indica momento ideal para investimentos pessoais."
        },
        "gemeos": {
            "diario": "Comunicação é a tua força. Dia propício para novas conexões.",
            "amor": "Paixão e diálogo caminham juntos. Momento mágico para confessar sentimentos.",
            "carreira": "Oportunidades surgem através de conversas. Rede de contactos é ouro.",
            "sorte": "Número 5 | Cor: Amarelo-ouro",
            "conselho_vip": "Mercúrio retrógrado termina em breve. Prepara-te para mudanças positivas."
        },
        "cancer": {
            "diario": "Emoções à flor da pele. Dia para cuidar de ti e dos teus.",
            "amor": "Profundidade emocional marca o dia. Segue o coração.",
            "carreira": "Intuição guia decisões importantes. Confias nela?",
            "sorte": "Número 2 | Cor: Prata-lunar",
            "conselho_vip": "Lua cheia energiza transformações internas. Reflexão e renovação."
        },
        "leao": {
            "diario": "Criatividade em alta. Dia para brilhares e mostrares o teu talento.",
            "amor": "Autoconfiança atrai admiradores. Momento de genuinidade.",
            "carreira": "Teu carisma abre portas. Liderança é natural hoje.",
            "sorte": "Número 1 | Cor: Ouro-solar",
            "conselho_vip": "Sol em aspecto maior potencia magnetismo pessoal. Aproveita a influência."
        },
        "virgem": {
            "diario": "Organização e clareza mental. Dia para resolver pendências.",
            "amor": "Pragmatismo encontra romance. Simplicidade é beleza.",
            "carreira": "Detalhes fazem a diferença. Teu trabalho brilha.",
            "sorte": "Número 6 | Cor: Verde-sálvia",
            "conselho_vip": "Mercúrio em harmonia potencia análise e comunicação eficaz."
        },
        "libra": {
            "diario": "Equilíbrio e harmonia dominam. Dia de decisões ponderadas.",
            "amor": "Beleza em tudo. Relações ganham profundidade e compreensão.",
            "carreira": "Diplomacia abre caminhos. Trabalhos em equipa florescem.",
            "sorte": "Número 7 | Cor: Azul-céu",
            "conselho_vip": "Vénus em posição forte eleva carisma e capacidade de atração."
        },
        "escorpiao": {
            "diario": "Poder interior intenso. Dia para transformações significativas.",
            "amor": "Paixão profunda e mistério. Intensidade emocional marca conexões.",
            "carreira": "Estratégia e determinação. Nada detém os teus objetivos.",
            "sorte": "Número 8 | Cor: Vermelho-sangue",
            "conselho_vip": "Plutão amplifica poder transformador. Renascimento pessoal próximo."
        },
        "sagitario": {
            "diario": "Liberdade e aventura chamam. Dia para explorar novos horizontes.",
            "amor": "Otimismo atrai pessoas. Momento para confessar sentimentos.",
            "carreira": "Expansão e crescimento. Riscos calculados levam ao sucesso.",
            "sorte": "Número 9 | Cor: Roxo-ametista",
            "conselho_vip": "Júpiter favorece oportunidades de crescimento e aprendizado significativo."
        },
        "capricornio": {
            "diario": "Dedicação com foco. Dia produtivo e realista.",
            "amor": "Compromisso verdadeiro. Relacionamentos ganham solidez.",
            "carreira": "Responsabilidade traz recompensas. Progresso constante.",
            "sorte": "Número 3 | Cor: Cinzento-grafite",
            "conselho_vip": "Saturno em transição favorece consolidação de objetivos a longo prazo."
        },
        "aquario": {
            "diario": "Inovação e originalidade. Dia para ideias revolucionárias.",
            "amor": "Independência e liberdade. Conexões autênticas surgem.",
            "carreira": "Pensamento criativo resolve desafios. Teu valor é reconhecido.",
            "sorte": "Número 11 | Cor: Azul-elétrico",
            "conselho_vip": "Urano potencia visão futurista e capacidade inovadora. Sincronicidades positivas."
        },
        "peixes": {
            "diario": "Intuição e criatividade fluem. Dia mágico e inspirador.",
            "amor": "Sensibilidade profunda. Empatia une corações.",
            "carreira": "Criatividade resolve desafios. Teu talento brilha sutilmente.",
            "sorte": "Número 12 | Cor: Verde-água",
            "conselho_vip": "Netuno amplifica sensibilidade intuitiva. Conexões espirituais se aprofundam."
        },
    }
    
    signo_normalizado = normalizar_signo(signo)

    # Retorna os dados do signo solicitado ou um padrão genérico para o teste
    return dados_api_externa.get(signo_normalizado, {
        "diario": f"Previsão diária geral para {signo}. O cosmos guia os teus passos.",
        "amor": "Grandes conexões emocionais estão a caminho.",
        "carreira": "Foca na organização e colherás os frutos.",
        "sorte": "Número 11 | Cor: Amarelo",
        "conselho_vip": "O teu mapa astral indica uma mudança de ciclo. Confia no processo."
    })


class RegisterModel(BaseModel):
    nome: str
    email: EmailStr
    password: str
    signo: str = "Aries"


class LoginModel(BaseModel):
    email: EmailStr
    password: str


class CheckoutSessionModel(BaseModel):
    plano: str


@app.post("/api/auth/register")
async def register(req: RegisterModel):
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="A senha deve ter pelo menos 8 caracteres.")

    email = req.email.lower()
    if get_user_by_email(email):
        raise HTTPException(status_code=409, detail="Email já registado.")

    user_id = str(uuid.uuid4())
    now = agora_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO users (id, nome, email, password_hash, signo, plano, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, req.nome.strip(), email, hash_password(req.password), req.signo.strip(), "basic", now, now),
        )

    token = issue_token(user_id)
    user = get_user_by_token(token)

    return {
        "access_token": token,
        "token_type": BEARER_AUTH_TYPE,
        "user": user_to_payload(user),
    }


@app.post("/api/auth/login")
async def login(req: LoginModel):
    user = get_user_by_email(req.email.lower())
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos.")

    token = issue_token(user["id"])
    updated_user = get_user_by_token(token)

    return {
        "access_token": token,
        "token_type": BEARER_AUTH_TYPE,
        "user": user_to_payload(updated_user),
    }


@app.get("/api/me")
async def me(user=Depends(get_current_user)):
    return {"user": user_to_payload(user)}


@app.get("/api/me/export")
async def export_me(user=Depends(get_current_user)):
    with get_db() as conn:
        sessions = conn.execute(
            """
            SELECT id, plano, status, provider, provider_session_id, created_at, completed_at
            FROM checkout_sessions
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user["id"],),
        ).fetchall()

    return {
        "user": user_to_payload(user),
        "checkout_sessions": [dict(row) for row in sessions],
        "exported_at": agora_iso(),
    }


@app.delete("/api/me")
async def delete_me(user=Depends(get_current_user)):
    with get_db() as conn:
        conn.execute("DELETE FROM checkout_sessions WHERE user_id = ?", (user["id"],))
        conn.execute("DELETE FROM users WHERE id = ?", (user["id"],))

    _append_data_request({
        "tipo": "account_deletion_completed",
        "user_id": user["id"],
        "email_hash": hashlib.sha256(user["email"].lower().encode("utf-8")).hexdigest(),
        "timestamp": agora_iso(),
    })
    return {"status": "deleted"}


@app.post("/api/checkout/session")
async def create_checkout_session(req: CheckoutSessionModel, user=Depends(get_current_user)):
    plano = normalizar_plano(req.plano)
    if plano == "basic":
        raise HTTPException(status_code=400, detail="Checkout disponível apenas para Premium ou VIP.")

    price_id = stripe_price_for_plan(plano)
    customer_id = get_or_create_stripe_customer(user)
    stripe_session = create_stripe_checkout_session(user, plano, price_id, customer_id)
    stripe_session_id = _stripe_obj_value(stripe_session, "id")
    checkout_url = _stripe_obj_value(stripe_session, "url")

    if not checkout_url:
        raise HTTPException(status_code=502, detail="Stripe não retornou URL de checkout.")

    session_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO checkout_sessions
                (id, user_id, plano, status, provider, provider_session_id, checkout_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, user["id"], plano, "pending", "stripe", stripe_session_id, checkout_url, agora_iso()),
        )

    return {
        "session_id": session_id,
        "stripe_session_id": stripe_session_id,
        "plano": plano,
        "status": "pending",
        "checkout_url": checkout_url,
    }


@app.post("/api/checkout/confirm")
async def confirm_checkout_session():
    raise HTTPException(status_code=410, detail="Confirmação manual removida. Use o webhook da Stripe.")


@app.post("/api/billing/portal")
async def billing_portal(user=Depends(get_current_user)):
    customer_id = get_or_create_stripe_customer(user)
    portal_session = create_stripe_portal_session(customer_id)
    return {"portal_url": _stripe_obj_value(portal_session, "url")}


@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: Optional[str] = Header(default=None, alias="Stripe-Signature")):
    event = _parse_stripe_event(await request.body(), stripe_signature)
    event_type = _stripe_obj_value(event, "type")
    data = _stripe_obj_value(event, "data", {}) or {}
    obj = _stripe_obj_value(data, "object", {}) or {}

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(obj)
    elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        _handle_subscription_changed(obj)

    return {"received": True}


@app.get("/api/horoscopo")
async def obter_horoscopo(signo: str, plano: str = "basic", authorization: Optional[str] = Header(default=None)):
    """
    Rota principal que o Frontend vai chamar.
    Filtra as informações com base no plano do utilizador (basic, premium, vip).
    """
    plano_usuario = normalizar_plano(plano)
    user = get_optional_user(authorization)
    plano_ativo = user["plano"] if user else "basic"

    if PLANOS_VALIDOS[plano_usuario] > PLANOS_VALIDOS[plano_ativo]:
        raise HTTPException(status_code=402, detail=f"Plano {plano_usuario} requer assinatura ativa.")

    # 1. Busca todos os dados da API Externa
    dados_completos = buscar_dados_astrologicos(signo)
    
    # 2. Estrutura a resposta de acordo com o nível de acesso (Paywall)
    resposta = {
        "signo": signo.capitalize(),
        "plano_consultado": plano_usuario,
        "previsao_diaria": dados_completos["diario"]
    }
    
    # Nível Premium (R$ 49,90) - Adiciona Amor e Carreira
    if plano_usuario in ["premium", "vip"]:
        resposta["amor"] = dados_completos["amor"]
        resposta["carreira"] = dados_completos["carreira"]
        
    # Nível VIP (R$ 150,00) - Adiciona Sorte e Conselho Profundo
    if plano_usuario == "vip":
        resposta["dados_da_sorte"] = dados_completos["sorte"]
        resposta["conselho_mistico_vip"] = dados_completos["conselho_vip"]
        
    return resposta

@app.get("/")
async def root():
    return {"message": f"{APP_NAME} - Backend ativo"}

@app.get("/api/metricas")
async def obter_metricas():
    """
    Retorna dados gerais do produto sem prova social inventada.
    """
    return {
        "signos_disponiveis": 12,
        "planos_disponiveis": 3,
        "app_instalavel": True,
        "categorias": ["diario", "amor", "carreira", "sorte"]
    }


# --- LGPD helpers and endpoints ---
data_requests_path_env = os.environ.get("DATA_REQUESTS_PATH")
DATA_REQUESTS_PATH = resolve_project_path(data_requests_path_env) if data_requests_path_env else os.path.join(RUNTIME_DIR, "data_requests.json")

def _append_data_request(item: dict):
    """Append a request to a local JSON file for audit/tracking.
    This is a simple implementation for development; in production use a secure database and audit logs.
    """
    try:
        if os.path.exists(DATA_REQUESTS_PATH):
            with open(DATA_REQUESTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []

    data.append(item)

    with open(DATA_REQUESTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class DataRequestModel(BaseModel):
    email: EmailStr
    detalhe: Optional[str] = None


@app.post("/api/request_data_deletion")
async def request_data_deletion(req: DataRequestModel):
    """Recebe solicitação de eliminação de dados pelo titular (LGPD).
    Em ambiente real, validar identidade do solicitante antes de processar.
    """
    item = {
        "tipo": "deletion",
        "email": req.email,
        "detalhe": req.detalhe,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    _append_data_request(item)
    return {"status": "received", "message": "Solicitação de eliminação recebida. Iremos processar e confirmar por email."}


@app.post("/api/request_data_portability")
async def request_data_portability(req: DataRequestModel):
    """Recebe solicitação de portabilidade (exportação) de dados pelo titular (LGPD)."""
    item = {
        "tipo": "portability",
        "email": req.email,
        "detalhe": req.detalhe,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    _append_data_request(item)
    return {"status": "received", "message": "Solicitação de portabilidade recebida. Prepararemos os dados e enviaremos por e-mail."}


class ConsentModel(BaseModel):
    email: EmailStr
    consent: bool


@app.post("/api/consent")
async def record_consent(req: ConsentModel):
    """Regista o consentimento do utilizador para fins de auditoria LGPD."""
    item = {
        "tipo": "consent",
        "email": req.email,
        "consent": bool(req.consent),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    _append_data_request(item)
    return {"status": "ok", "message": "Consentimento registado."}


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    reload = bool(os.environ.get("DEV", "").lower() in {"1", "true", "yes"})
    uvicorn.run("main:app", host=host, port=port, reload=reload)
