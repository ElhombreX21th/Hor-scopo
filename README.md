# SeuFuturo

SaaS de previsões astrológicas com backend FastAPI, frontend PWA responsivo, autenticação, paywall por plano e assinatura recorrente via Stripe Checkout.

## Estrutura

```text
Horoscopo/
├── backend/
│   ├── main.py              # API, autenticação, paywall, Stripe e LGPD
│   ├── requirements.txt      # Dependências Python
│   └── test_main.py          # Testes de auth, paywall, Stripe e signos
├── frontend/
│   ├── index.html            # App PWA
│   ├── manifest.json
│   ├── service-worker.js
│   ├── privacy.html
│   └── terms.html
├── .env.example
└── README.md
```

## Configuração Local

1. Copia `.env.example` para `.env` e preenche as chaves Stripe.

2. Instala e executa o backend:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

3. Executa o frontend:

```bash
python -m http.server 8001 --directory frontend
```

URLs locais:

- Frontend: `http://127.0.0.1:8001`
- Backend: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

## Variáveis de Produção

Obrigatórias para pagamento real:

- `APP_BASE_URL`: URL pública do frontend, ex. `https://hypersecit.com.br`
- `ALLOWED_ORIGINS`: origens CORS, ex. `https://hypersecit.com.br`
- `STRIPE_SECRET_KEY`: chave secreta Stripe
- `STRIPE_PRICE_PREMIUM`: ID do Price recorrente Premium
- `STRIPE_PRICE_VIP`: ID do Price recorrente VIP
- `STRIPE_WEBHOOK_SECRET`: segredo do webhook Stripe

O domínio de produção configurado no projeto é:

```text
https://hypersecit.com.br
```

O webhook público deve apontar para:

```text
POST https://hypersecit.com.br/api/stripe/webhook
```

Eventos Stripe usados:

- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`

## Planos

| Plano | Preço sugerido | Funcionalidades |
|---|---:|---|
| Basic | Grátis | Previsão diária |
| Premium | R$ 49,90/mês | Amor + carreira |
| VIP | R$ 150,00/mês | Tudo + sorte e conselho místico |

## Endpoints Principais

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/me`
- `GET /api/horoscopo?signo=Aries&plano=basic`
- `POST /api/checkout/session`
- `POST /api/billing/portal`
- `POST /api/stripe/webhook`
- `POST /api/request_data_deletion`
- `POST /api/request_data_portability`

## Testes

```bash
pytest backend/test_main.py -q
```

Cobertura atual:

- Premium/VIP bloqueados sem assinatura ativa
- Checkout Stripe cria sessão e não libera plano sozinho
- Webhook `checkout.session.completed` libera Premium/VIP
- Webhook de cancelamento volta o usuário para Basic
- Customer Portal retorna URL Stripe
- Signos com acentos/nomes PT usam previsões corretas

## Checklist Antes de Publicar

- Criar produtos e preços recorrentes no Stripe.
- Configurar webhook com `STRIPE_WEBHOOK_SECRET`.
- Hospedar backend em HTTPS.
- Hospedar frontend em HTTPS.
- Definir `ALLOWED_ORIGINS` com domínio final.
- Trocar SQLite por PostgreSQL se houver tráfego real.
- Configurar política de privacidade, termos e emails reais.
- Validar o PWA no Lighthouse/PWABuilder.

## Notas

- O backend ainda usa dados simulados de astrologia. A integração real deve substituir `buscar_dados_astrologicos`.
- O plano pago só é ativado por webhook Stripe, não por resposta do frontend.
- O endpoint antigo `/api/checkout/confirm` retorna `410` e não libera assinatura manualmente.
