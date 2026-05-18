# Data Safety / App Privacy

Use este arquivo como base para preencher Google Play Data Safety e Apple App Privacy. Ajustar se novos SDKs, analytics, ads ou provedores forem adicionados.

## Dados coletados

- Nome: usado para conta e personalizacao.
- Email: usado para login, conta, suporte, assinatura e solicitacoes LGPD.
- Signo/plano escolhido: usado para personalizar previsoes e controlar acesso.
- Historico de compra/assinatura: plano, status, IDs de checkout e eventos de provedor; nao inclui numero de cartao.
- Metricas tecnicas agregadas: usadas para operacao e melhoria do servico.

## Compartilhamento

- Provedores de pagamento: Stripe, PayPal e Mercado Pago quando usados no site/PWA.
- Hospedagem/infraestrutura: Vercel e banco configurado em producao.
- Email/suporte: apenas se configurado para comunicacao operacional.

Nao vender dados pessoais. Nao usar dados para publicidade comportamental. Nao configurar SDK de ads sem atualizar este arquivo e a politica publica.

## Finalidades

- Funcionalidade do app.
- Gerenciamento de conta.
- Processamento de pagamentos/assinaturas.
- Prevencao de fraude e seguranca.
- Atendimento de solicitacoes legais e LGPD.

## Seguranca e retencao

- Trafego em producao via HTTPS.
- Headers de seguranca configurados na API.
- Pagamentos processados por provedores externos; o app nao armazena dados completos de cartao.
- Exportacao de dados autenticada: `GET /api/me/export`.
- Exclusao de conta autenticada: `DELETE /api/me`.
- Formulario publico de solicitacao LGPD: `/privacy`.

## Apple App Privacy sugerido

- Contact Info: Name, Email Address. Linked to user. Used for App Functionality and Account Management.
- User Content / Other Data: zodiac sign and selected plan. Linked to user. Used for App Functionality.
- Purchases: subscription status and checkout identifiers. Linked to user. Used for App Functionality.
- Identifiers: internal user ID/session token. Linked to user. Used for App Functionality and Fraud Prevention.
- Tracking: No.
- Data used for third-party advertising: No.

## Google Play Data Safety sugerido

- Personal info: name, email address. Collected. Not sold. Used for account management and app functionality.
- Financial info: purchase history/subscription status only. Collected. Payment card data handled by payment providers.
- App activity: app interactions/sign selection/plan selection. Collected for app functionality and analytics.
- Device or other IDs: only if introduced by future analytics, billing SDKs, or push providers.
- Data deletion: available by authenticated account deletion and privacy form.

