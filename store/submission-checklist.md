# Submission Checklist

## Antes de criar os apps nas lojas

- [ ] Confirmar `br.com.hypersecit.seufuturo` como package/bundle ID.
- [ ] Confirmar nome publico `SeuFuturo`.
- [ ] Confirmar email publico de suporte.
- [ ] Confirmar conta Apple Developer ativa.
- [ ] Confirmar conta Google Play Developer ativa e verificada.
- [ ] Confirmar dados fiscais e bancarios nas duas lojas.
- [ ] Confirmar politica de privacidade e termos publicados.

## Google Play

- [ ] Criar app no Play Console.
- [ ] Configurar app como gratis.
- [ ] Enviar icon 512x512 e feature graphic 1024x500.
- [ ] Preencher descricao curta/completa em `store/google-play/listing-pt-BR.md`.
- [ ] Preencher Data Safety usando `store/privacy/data-safety-and-app-privacy.md`.
- [ ] Criar produtos de assinatura no Play Billing.
- [ ] Gerar Android App Bundle (AAB) assinado.
- [ ] Subir primeiro para Internal testing.
- [ ] Validar login, assinatura, exportacao e exclusao de dados.

## App Store

- [ ] Criar Bundle ID.
- [ ] Criar app record no App Store Connect.
- [ ] Enviar icon 1024x1024 e screenshots.
- [ ] Preencher descricao em `store/app-store/listing-pt-BR.md`.
- [ ] Preencher App Privacy usando `store/privacy/data-safety-and-app-privacy.md`.
- [ ] Criar In-App Purchases/Subscriptions no App Store Connect.
- [ ] Gerar build assinado.
- [ ] Subir para TestFlight antes de App Review.
- [ ] Validar login, assinatura, exportacao e exclusao de dados.

## Producao

- [ ] Migrar SQLite efemero da Vercel para Postgres/Neon/Supabase antes de trafego real.
- [ ] Configurar secrets reais de Stripe/PayPal/Mercado Pago/Apple/Google por ambiente.
- [ ] Configurar webhooks/notifications de assinatura.
- [ ] Rodar testes automatizados.
- [ ] Rodar auditoria de dependencias.
- [ ] Fazer smoke test no deployment de producao.

