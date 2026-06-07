# SeuFuturo Store Submission Pack

Este diretorio concentra o material para publicar o SeuFuturo na App Store e na Google Play com o dominio oficial `https://seufuturo.blog.br/`.

## Estrategia da primeira versao

A primeira versao nativa esta preparada como app gratuito com o plano Basic. PayPal e PIX continuam disponiveis no site/PWA, mas ficam bloqueados no build de loja para evitar rejeicao por compra externa de conteudo digital.

Quando quiser vender Premium/VIP dentro dos apps nativos, implemente:

- iOS: StoreKit / In-App Purchase.
- Android: Google Play Billing.

Produtos planejados para a etapa seguinte:

- `seufuturo_premium_monthly`
- `seufuturo_vip_monthly`

## URLs publicas

- App: https://seufuturo.blog.br/
- Manifest: https://seufuturo.blog.br/manifest.json
- Politica de privacidade: https://seufuturo.blog.br/privacy
- Termos: https://seufuturo.blog.br/terms

## Identificadores

- Android package name: `br.blog.seufuturo`
- iOS bundle ID: `br.blog.seufuturo`
- App name: `SeuFuturo`
- Categoria sugerida: `Lifestyle` / `Estilo de vida`

Esses identificadores ficam permanentes depois que os apps forem criados nas lojas.

## Build nativo

O projeto usa Capacitor para empacotar a PWA:

```bash
npm install
npm run build:store
```

Comandos por plataforma:

```bash
npm run ios:open
npm run android:open
npm run android:bundle:win
```

Observacao: o upload iOS exige macOS com Xcode. No Windows da para preparar o projeto, gerar assets, validar o Android e abrir a pasta iOS para levar ao Mac.

## Assets

- App Store icon 1024x1024: `store/assets/app-icon-1024.png`
- Google Play icon 512x512: `store/assets/google-play-icon-512.png`
- Google Play feature graphic 1024x500: `store/assets/feature-graphic-1024x500.png`
- App Store screenshots: `store/screenshots/app-store/*.png`
- Google Play screenshots: `store/screenshots/google-play/*.png`
- PWA icons publicados: `frontend/icons/*.png`

Regenerar screenshots:

```bash
npm run store:screenshots
```

Validar o pacote antes de submeter:

```bash
npm run store:check
```

## Documentos

- App Store: `store/app-store/listing-pt-BR.md`
- Build e envio iOS: `store/app-store/build-and-submit.md`
- Google Play: `store/google-play/listing-pt-BR.md`
- Build e envio Android: `store/google-play/build-and-submit.md`
- Privacidade/Data Safety: `store/privacy/data-safety-and-app-privacy.md`
- Checklist geral: `store/submission-checklist.md`
