# Instruções Rápidas de Deploy

Objetivo: deixar a aplicação pronta para apontar um domínio e publicar (backend FastAPI + frontend estático).

Opções recomendadas:

- Docker + Docker Compose (recomendado para VPS ou serviços que suportem containers)
- Deploy em PaaS (Heroku, Render, Railway) usando `Procfile` ou Docker

## Vercel + dominio HYPERSECIT.COM.BR

O repo ja inclui configuracao para deploy na Vercel:

- `vercel.json` envia `/`, `/manifest.json`, `/service-worker.js`, `/privacy` e `/terms` para o frontend em `frontend/`.
- `/api/*`, `/docs` e `/openapi.json` sao enviados para o FastAPI serverless em `api/index.py`.
- `.vercelignore` evita enviar banco SQLite local, logs e caches.

Fluxo recomendado:

1. Importe o repo GitHub na Vercel.
2. Configure o projeto como "Other" se a Vercel nao detectar automaticamente.
3. Adicione as variaveis de ambiente de producao:

```text
APP_NAME=SeuFuturo
APP_BASE_URL=https://hypersecit.com.br
ALLOWED_ORIGINS=https://hypersecit.com.br
ADMIN_TOKEN=<token forte>
STRIPE_SECRET_KEY=<sk_live_...>
STRIPE_PRICE_PREMIUM=<price_...>
STRIPE_PRICE_VIP=<price_...>
STRIPE_WEBHOOK_SECRET=<whsec_...>
```

4. Adicione o dominio `hypersecit.com.br` no projeto Vercel.
5. No DNS do dominio, use os valores exibidos pela Vercel. Valores gerais documentados:
   - apex/root `hypersecit.com.br`: registro `A` para `76.76.21.21`
   - `www.hypersecit.com.br`: registro `CNAME` para `cname.vercel-dns-0.com`
6. Configure o webhook Stripe em `https://hypersecit.com.br/api/stripe/webhook`.

Importante: SQLite em Vercel usa armazenamento efemero. Para assinaturas reais persistentes, migre para Postgres/Neon/Supabase antes de trafego real.

Passos com Docker (testes locais):

1. Certifique-se de ter `docker` e `docker-compose` instalados.

2. Build e up:

```bash
docker-compose build
docker-compose up -d
```

3. Acesse:
- Frontend: https://hypersecit.com.br
- Backend: http://localhost:8000

Produção com domínio e HTTPS:

1. Obtenha uma VPS (DigitalOcean, Linode, AWS EC2) ou use um provedor de containers (Render, Railway, Fly.io).

2. Aponte o DNS do teu domínio (A record) para o IP da VPS.

3. No servidor, clone o repositório e rode o `docker-compose` (como acima).

4. Configure um proxy reverso (nginx/Caddy) para mapear o domínio final:

- `https://hypersecit.com.br` -> frontend na raiz
- `https://hypersecit.com.br/api/*` -> backend
- `https://hypersecit.com.br/docs` e `https://hypersecit.com.br/openapi.json` -> backend

5. Recomendado: usar Caddy ou Certbot + nginx para TLS automático. Exemplo com Caddy (Caddyfile):

```
hypersecit.com.br {
  handle /api/* {
    reverse_proxy localhost:8000
  }

  handle /docs* {
    reverse_proxy localhost:8000
  }

  handle /openapi.json {
    reverse_proxy localhost:8000
  }

  handle {
    reverse_proxy localhost:8001
  }
}
```

Variáveis de ambiente importantes (backend):

- `PORT` - porta onde o backend escuta (padrão 8000)
- `HOST` - host (padrão 0.0.0.0)
- `HOROSCOPO_DB_PATH` - caminho para o DB SQLite
- `APP_BASE_URL` - URL base usada em callbacks e links
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PREMIUM`, `STRIPE_PRICE_VIP` - se usar Stripe

Pagamento — como configurar e vincular provedores

- Stripe (cartões de crédito/débito, cartões brasileiros, e opções de pagamento locais dependendo da conta):
  1. Crie conta em https://dashboard.stripe.com (modo Test/Live).
  2. Obtenha `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET` e configure no servidor/serviço (variáveis de ambiente).
  3. Já existe implementação de Checkout para assinaturas em `/api/checkout/session` — o frontend apenas redireciona para a `checkout_url` retornada.

- PayPal (checkout com redirect ou pop-up):
  1. Crie conta Business em https://developer.paypal.com/ e gere `PAYPAL_CLIENT_ID` e `PAYPAL_SECRET` (sandbox para testes).
  2. Defina `PAYPAL_MODE` como `sandbox` ou `live` no ambiente.
  3. Endpoints já adicionados no backend:
     - `POST /api/paypal/create-order` — cria uma ordem. Enviar JSON: `{ "amount": "49.90", "currency": "BRL", "return_url": "https://...", "cancel_url": "https://..." }`.
     - `POST /api/paypal/capture/{order_id}` — captura a ordem após aprovação.
  4. Fluxo típico: frontend chama `create-order`, redireciona o utilizador para o link `approve` retornado, após aprovação chama `capture` no backend para finalizar.

- PIX (opções no Brasil):
  - Opção 1 — Mercado Pago (suporta PIX, boleto, cartão): crie conta em https://www.mercadopago.com.br/, gere Access Token e configure no ambiente (ex: `MP_ACCESS_TOKEN`). Use a API de pagamentos do Mercado Pago para gerar QR Code PIX. Existe SDK oficial (`mercadopago`) ou usar `requests` para chamar a API.
  - Opção 2 — Gerencianet / Pagar.me / outros provedores brasileiros: cada provedor tem própria API para gerar QR Codes PIX e webhooks.
  - Recomendo Mercado Pago para facilidade: criar preferência/ pagamento PIX e retornar o QR code para o frontend.

Variáveis adicionais para pagamentos:

- `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`, `PAYPAL_MODE` (sandbox|live)
- `MP_ACCESS_TOKEN` (MercadoPago) — se optar por Mercado Pago
- `GERENCIANET_CLIENT_ID` / `GERENCIANET_CLIENT_SECRET` — se optar por Gerencianet

Admin (reembolsos e auditoria):

- `ADMIN_TOKEN` — token secreto usado para proteger endpoints administrativos (`/api/admin/*`). Configure uma string forte como variável de ambiente no servidor.
- Use `curl` com header `Authorization: Bearer <ADMIN_TOKEN>` para chamar `/api/admin/refund` e `/api/admin/requests`.

Segurança e webhooks:

- Registe os endpoints de webhook no painel do provedor (Stripe/PayPal/MercadoPago) apontando para `/api/stripe/webhook`, endpoints PayPal webhooks (se desejar) e o endpoint do MercadoPago que criarás.
- Use HTTPS em produção e valide assinaturas dos webhooks (ex: `STRIPE_WEBHOOK_SECRET`).

Exemplo rápido (PayPal):

```bash
# criar ordem
curl -X POST https://api-m.sandbox.paypal.com/v2/checkout/orders \
 -H "Authorization: Bearer <TOKEN>" \
 -H "Content-Type: application/json" \
 -d '{"intent":"CAPTURE","purchase_units":[{"amount":{"currency_code":"BRL","value":"49.90"}}]}'
```

Se quiser, implemento também um endpoint de webhook PayPal e um exemplo completo de geração de PIX via Mercado Pago no `backend/` — quer que eu adicione ambos agora?

Webhooks e configuração (PayPal / Mercado Pago)

1. PayPal
  - No painel do PayPal (developer), registe o URL do webhook: `https://hypersecit.com.br/api/paypal/webhook`.
  - Configure os eventos que deseja receber (ex.: `PAYMENT.CAPTURE.COMPLETED`, `CHECKOUT.ORDER.APPROVED`).
  - Em produção, valida a assinatura do webhook usando o SDK do PayPal ou com as headers fornecidas. O backend já guarda os eventos em `backend/data_requests.json` para auditoria.

2. Mercado Pago (PIX)
  - No painel Mercado Pago, configure o webhook apontando para `https://hypersecit.com.br/api/mercadopago/webhook`.
  - Use a variável `MP_ACCESS_TOKEN` no ambiente para que o backend possa criar pagamentos PIX via `POST /api/mercadopago/create-pix`.
  - O endpoint retorna `qr_code` e `qr_code_base64` para exibir ao utilizador.

Segurança:
- Sempre use HTTPS para webhooks.
- Valide assinaturas dos provedores quando possível (PayPal/MercadoPago/Stripe).
- Teste no modo sandbox antes de mudar para modo `live`.

Logs e monitorização

- O backend escreve logs em `backend/logs/backend.log`. Garanta que o diretório tem permissão de escrita pelo serviço que executar a aplicação.
- Recomendado: configure `logrotate` ou um serviço de logs (Papertrail, LogDNA, Datadog) para evitar disco cheio.
- Habilite alertas para falhas em webhooks e taxas de erro altas.

Instalar `systemd` unit e `logrotate` (exemplo)

1. Copie `deploy/seufuturo.service` para `/etc/systemd/system/seufuturo.service` e ajuste `WorkingDirectory`, `User`, `Environment` com as tuas variáveis reais.

```bash
sudo cp deploy/seufuturo.service /etc/systemd/system/seufuturo.service
sudo systemctl daemon-reload
sudo systemctl enable seufuturo
sudo systemctl start seufuturo
sudo journalctl -u seufuturo -f
```

2. Copie `deploy/seufuturo-logrotate.conf` para `/etc/logrotate.d/seufuturo`:

```bash
sudo cp deploy/seufuturo-logrotate.conf /etc/logrotate.d/seufuturo
sudo logrotate -d /etc/logrotate.d/seufuturo
```

Certifique-se de que o `User` no `systemd` tem permissão de escrita no diretório de logs e no `HOROSCOPO_DB_PATH`.

Script de deploy automático

Incluí um script de deploy simples em `deploy/deploy.sh` que realiza:

- Clone ou atualiza o repositório em um diretório alvo (padrão `/opt/seufuturo`).
- Reconstrói imagens Docker e sobe os serviços via `docker-compose` / `docker compose`.
- Opção para instalar o `systemd` unit se executado como root.

Como usar (no servidor):

```bash
# torne executável
chmod +x deploy/deploy.sh
# executar (diretório e branch opcionais)
./deploy/deploy.sh /opt/seufuturo main
```

O script espera que as variáveis de ambiente estejam em um arquivo `.env` no diretório do projeto ou que você as configure no ambiente do sistema (por exemplo, `/etc/environment` ou systemd unit). Há um arquivo de exemplo `.env.example` na raiz do projeto com variáveis necessárias.

Deploy remoto via SSH

Incluí um script `deploy/deploy_remote.sh` que automatiza o envio do código para um servidor remoto e executa `deploy/deploy.sh` lá.

Como usar (do seu computador local):

```bash
# gere um .env local com as variáveis de produção/sandbox
# envie o código e execute o deploy remoto
chmod +x deploy/deploy_remote.sh
./deploy/deploy_remote.sh user@host /opt/seufuturo main /path/to/.env
```

O script realiza:
- cria um tarball do branch especificado;
- envia o tarball para `/tmp` no servidor remoto via `scp`;
- extrai o conteúdo em `TARGET_DIR` (por padrão `/opt/seufuturo`);
- envia o `.env` informado para `TARGET_DIR/.env` (se fornecido);
- executa `deploy/deploy.sh` no host remoto.

Requisitos no servidor remoto:
- `docker` e `docker-compose` (ou `docker compose`);
- usuário com permissão para executar docker (ou executar como root);
- SSH configurado e acessível (chave pública preferível).

Segurança: não armazene chaves secretas em repositórios. Use `ssh-agent`, chaves de deploy, ou variáveis de ambiente no `systemd` unit.

Deploy para Heroku (rápido):

1. Faça login no Heroku e crie um app.
2. Faça push do repositório (ou use container registry).
3. Defina variáveis de ambiente no painel do Heroku.

Comandos úteis:

```bash
# Build & start com docker-compose
docker-compose up -d --build

# Ver logs
docker-compose logs -f backend

# Parar
docker-compose down
```

Se quiser, posso configurar um `nginx` de reverse-proxy exemplo e um `Caddyfile` pronto para teu domínio — quer que eu gere esses arquivos também?
