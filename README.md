# SeuFuturo

SaaS de previsões astrológicas com backend FastAPI, frontend PWA responsivo, autenticação, paywall por plano e pagamentos via PayPal e PIX/Mercado Pago.

## Projeto Vercel Exclusivo

O SeuFuturo fica isolado no projeto Vercel `seufuturo-horoscopo`.

URL pública final:

```text
https://seufuturo.blog.br
```

Não use domínios ou projetos de outros produtos para este app. O domínio `seufuturo.blog.br` deve ficar anexado apenas ao projeto Vercel `seufuturo-horoscopo`.

## Estrutura

```text
SeuFuturo/
├── backend/
│   ├── main.py              # API, autenticação, paywall, pagamentos e LGPD
│   ├── requirements.txt      # Dependências Python
│   └── test_main.py          # Testes de auth, paywall, pagamentos e signos
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

1. Copia `.env.example` para `.env` e preenche as chaves dos provedores de pagamento.

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

- `APP_BASE_URL`: URL pública do frontend, ex. `https://seufuturo.blog.br`
- `ALLOWED_ORIGINS`: origens CORS, ex. `https://seufuturo.blog.br`
- `PAYPAL_MODE`: `live` em produção ou `sandbox` em testes
- `PAYPAL_CLIENT_ID`: client ID do PayPal
- `PAYPAL_SECRET`: secret do PayPal
- `PAYPAL_WEBHOOK_ID`: webhook ID do PayPal
- `MP_ACCESS_TOKEN`: access token do Mercado Pago
- `MP_WEBHOOK_URL`: URL pública do webhook PIX

O domínio de produção configurado no projeto é:

```text
https://seufuturo.blog.br
```

O webhook público do Mercado Pago deve apontar para:

```text
POST https://seufuturo.blog.br/api/mercadopago/webhook
```

## Deploy na Vercel

O projeto esta preparado para Vercel com:

- `vercel.json` roteando o frontend estatico em `/` e FastAPI em `/api/*`.
- `api/index.py` como entrada serverless Python.
- `.vercelignore` removendo bancos locais, logs e caches do deploy.
- `requirements.txt` na raiz com as dependências Python usadas pela função serverless.

Variaveis recomendadas na Vercel:

```text
APP_NAME=SeuFuturo
APP_BASE_URL=https://seufuturo.blog.br
ALLOWED_ORIGINS=https://seufuturo.blog.br
ADMIN_TOKEN=<token forte>
DATABASE_URL=<postgres_url_neon_supabase_ou_vercel_storage>
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=<client_id>
PAYPAL_SECRET=<secret>
PAYPAL_WEBHOOK_ID=<webhook_id>
MP_ACCESS_TOKEN=<mercado_pago_access_token>
MP_WEBHOOK_URL=https://seufuturo.blog.br/api/mercadopago/webhook
```

Domínio:

- Projeto Vercel: `seufuturo-horoscopo`.
- Domínio de produção: `seufuturo.blog.br`.
- DNS necessário no provedor: `A seufuturo.blog.br 76.76.21.21`.
- DNS recomendado para `www`: `A www.seufuturo.blog.br 76.76.21.21`.
- Não reutilize domínio de outro produto.

Obrigatorio em producao na Vercel: configure `DATABASE_URL`, `POSTGRES_URL` ou `POSTGRES_URL_NON_POOLING` apontando para Postgres/Neon/Supabase/Vercel Storage. O backend bloqueia criacao/login de conta com `503` se estiver na Vercel usando SQLite temporario, para evitar perda de usuarios e falhas em PIX/cartao.

Pagamentos ativos no site/PWA:

- PayPal: criação de ordem, aprovação externa e captura.
- PIX/Mercado Pago: criação de cobrança PIX e confirmação por webhook.

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
- `POST /api/paypal/create-order`
- `POST /api/paypal/capture/{order_id}`
- `POST /api/mercadopago/create-pix`
- `POST /api/mercadopago/webhook`
- `POST /api/request_data_deletion`
- `POST /api/request_data_portability`

## Testes

```bash
pytest backend/test_main.py -q
```

Cobertura atual:

- Premium/VIP bloqueados sem assinatura ativa
- PayPal cria ordem e exige captura aprovada
- PIX gera cobrança Mercado Pago e aguarda confirmação
- Webhooks/eventos de pagamento controlam mudança de plano
- Signos com acentos/nomes PT usam previsões corretas

## Checklist Antes de Publicar

- Configurar PayPal em produção ou sandbox.
- Configurar Mercado Pago PIX e webhook público.
- Hospedar backend em HTTPS.
- Hospedar frontend em HTTPS.
- Definir `ALLOWED_ORIGINS` com domínio final.
- Trocar SQLite por PostgreSQL se houver tráfego real.
- Configurar política de privacidade, termos e emails reais.
- Validar o PWA no Lighthouse/PWABuilder.

## Notas

- O backend ainda usa dados simulados de astrologia. A integração real deve substituir `buscar_dados_astrologicos`.
- O plano pago só deve ser ativado por confirmação do provedor, não por resposta manual do frontend.
- O endpoint antigo `/api/checkout/confirm` retorna `410` e não libera assinatura manualmente.
