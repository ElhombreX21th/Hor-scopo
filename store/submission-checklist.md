# Submission Checklist

## Antes de criar os apps nas lojas

- [ ] Confirmar `br.blog.seufuturo` como Android package name e iOS bundle ID.
- [ ] Confirmar nome publico `SeuFuturo`.
- [ ] Confirmar email publico de suporte, hoje sugerido como `suporte@seufuturo.blog.br`.
- [ ] Confirmar conta Apple Developer ativa.
- [ ] Confirmar conta Google Play Developer ativa e verificada.
- [ ] Confirmar dados fiscais, bancarios e contratos nas lojas.
- [ ] Confirmar politica de privacidade e termos publicados em `https://seufuturo.blog.br/`.
- [ ] Rodar `npm run store:check`.

## App Store

- [ ] Criar Bundle ID `br.blog.seufuturo`.
- [ ] Criar app record no App Store Connect.
- [ ] Preencher descricao em `store/app-store/listing-pt-BR.md`.
- [ ] Enviar icon 1024x1024 e screenshots em `store/screenshots/app-store/`.
- [ ] Preencher App Privacy usando `store/privacy/data-safety-and-app-privacy.md`.
- [ ] No primeiro envio, manter app gratuito/Basic sem links de compra externa.
- [ ] Em um Mac, abrir `ios/App/App.xcworkspace` pelo Xcode.
- [ ] Configurar signing/capabilities com a equipe Apple.
- [ ] Gerar Archive e enviar para App Store Connect/TestFlight.
- [ ] Selecionar o build processado e enviar para App Review.

## Google Play

- [ ] Criar app no Play Console como gratuito.
- [ ] Preencher descricao em `store/google-play/listing-pt-BR.md`.
- [ ] Enviar icon 512x512, feature graphic 1024x500 e screenshots em `store/screenshots/google-play/`.
- [ ] Preencher Data Safety usando `store/privacy/data-safety-and-app-privacy.md`.
- [ ] Declarar app sem anuncios, se nenhum SDK de anuncios for adicionado.
- [ ] Criar keystore de release e preencher `android/key.properties`.
- [ ] Gerar Android App Bundle assinado (`.aab`).
- [ ] Subir primeiro para teste interno ou fechado.
- [ ] Se a conta pessoal foi criada depois de 13/11/2023, executar teste fechado com pelo menos 12 testers opt-in por 14 dias continuos antes de pedir acesso a producao.
- [ ] Enviar para revisao de producao depois do teste obrigatorio.

## Depois, para Premium/VIP nativos

- [ ] Criar assinaturas `seufuturo_premium_monthly` e `seufuturo_vip_monthly` na App Store.
- [ ] Criar assinaturas equivalentes no Google Play Billing.
- [ ] Implementar StoreKit no iOS e Google Play Billing no Android.
- [ ] Validar recibos/tokens no backend antes de liberar Premium/VIP.
- [ ] Configurar webhooks/server notifications das lojas.

## Producao

- [ ] Migrar SQLite efemero da Vercel para Postgres/Neon/Supabase antes de trafego real.
- [ ] Configurar secrets reais por ambiente.
- [ ] Rodar testes automatizados.
- [ ] Rodar auditoria de dependencias.
- [ ] Fazer smoke test em `https://seufuturo.blog.br/`.
