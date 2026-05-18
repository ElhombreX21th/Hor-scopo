# SeuFuturo Store Submission Pack

Estado atual: a PWA esta online em `https://seufuturo-phi.vercel.app/` e pronta para gerar pacotes nativos/TWA quando as contas Apple e Google estiverem autorizadas.

Sem pagar contas de loja agora, use a distribuicao gratuita por PWA:

- Link direto: `https://seufuturo-phi.vercel.app/`
- A instalacao acontece pelo navegador.
- O kit de divulgacao gratuita esta em `marketing/`.

O preparo de App Store/Google Play continua neste diretorio para quando voce decidir pagar as contas e seguir para submissao oficial.

## Links de autorizacao

- Google Play Console: https://play.google.com/console/
- Criar conta Google Play Developer: https://play.google.com/console/signup
- Apple Developer Program: https://developer.apple.com/programs/enroll/
- App Store Connect: https://appstoreconnect.apple.com/apps
- PWABuilder para gerar pacote PWA/TWA: https://www.pwabuilder.com/reportcard?site=https%3A%2F%2Fseufuturo-phi.vercel.app%2F

## URLs publicas

- App: https://seufuturo-phi.vercel.app/
- Manifest: https://seufuturo-phi.vercel.app/manifest.json
- Politica de privacidade: https://seufuturo-phi.vercel.app/privacy
- Termos: https://seufuturo-phi.vercel.app/terms

## Identificadores sugeridos

- Android package name: `br.com.hypersecit.seufuturo`
- iOS bundle ID: `br.com.hypersecit.seufuturo`
- App name: `SeuFuturo`
- Categoria: `Lifestyle`

O package name Android e o bundle ID iOS viram identificadores permanentes no ecossistema da loja. Confirmar antes de criar os registros oficiais.

## Assets gerados

- App Store icon: `store/assets/app-icon-1024.png`
- Google Play icon: `store/assets/google-play-icon-512.png`
- Google Play feature graphic: `store/assets/feature-graphic-1024x500.png`
- Screenshot Android: `store/screenshots/android-pixel-7.png`
- Screenshot iOS/web mobile: `store/screenshots/ios-phone-430x932.png`
- Screenshot wide/web: `store/screenshots/web-wide-1280x720.png`
- PWA icons publicados no frontend: `frontend/icons/*.png`

## Bloqueio de monetizacao nas lojas

Stripe, PayPal e PIX podem continuar no site/PWA. Para apps distribuidos pela App Store e Google Play, Premium/VIP sao conteudo digital dentro do app; por isso, o caminho seguro para aprovacao e usar:

- Apple: StoreKit / In-App Purchase para iOS.
- Google: Google Play Billing para Android.

Produtos sugeridos:

- `seufuturo_premium_monthly` -> plano Premium mensal.
- `seufuturo_vip_monthly` -> plano VIP mensal.

Depois que as contas estiverem liberadas, o proximo passo tecnico e criar os produtos nas lojas e adicionar verificacao server-side dos recibos/tokens antes de liberar `premium` ou `vip`.
