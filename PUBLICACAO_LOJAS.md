# 📱 Publicar SeuFuturo nas Lojas de Aplicativos

> Atualização de 2026-05-18: o pacote atual de publicação está em `store/`.
> Use `store/README.md`, `store/submission-checklist.md`, `store/google-play/listing-pt-BR.md`,
> `store/app-store/listing-pt-BR.md` e `store/privacy/data-safety-and-app-privacy.md` como fonte principal.
> Este arquivo fica como histórico/guia amplo.

## 🎯 Visão Geral

O SeuFuturo está pronto para ser distribuído como Progressive Web App (PWA) e pode ser publicado nas principais lojas de aplicativos móveis.

## 🛠️ O Que é PWA?

Uma **Progressive Web App** é uma aplicação web que funciona como um aplicativo nativo em dispositivos móveis:
- ✅ Funciona offline
- ✅ Notificações push
- ✅ Instalável na tela inicial
- ✅ Interface nativa
- ✅ Performance otimizada

## 📋 Requisitos para Publicação

### Google Play Store (Android)

1. **Criar conta Google Play Developer** ($25 USD)
   - Acesso: https://play.google.com/apps/publish

2. **Ferramentas necessárias:**
   - Android Studio (gratuito)
   - Bubblewrap CLI - converte PWA em APK Android
   - KeyStore para assinatura

3. **Passo a passo:**

```bash
# Instalar Bubblewrap CLI
npm install -g @bubblewrap/cli

# Criar projeto
bubblewrap init --manifest manifest.json

# Gerar APK assinado
bubblewrap build --release
```

4. **Arquivos gerados:**
   - `app-release.aab` (Android App Bundle) - mais moderno
   - `app-release.apk` - compatível com versões antigas

### Apple App Store (iOS)

1. **Criar Apple Developer Account** ($99 USD/ano)
   - Acesso: https://developer.apple.com/

2. **Ferramentas necessárias:**
   - Xcode (gratuito na App Store)
   - Apple Configurator 2
   - Certificate, Identifier & Profiles no Apple Developer

3. **Opção A: Usar Capacitor (Recomendado)**

```bash
# Instalar Capacitor
npm install -g @capacitor/cli
npm install @capacitor/core @capacitor/ios

# Criar projeto iOS
npx cap init seufuturo 'br.com.hypersecit.seufuturo'

# Adicionar iOS
npx cap add ios

# Compilar para iOS
npx cap build ios

# Abrir Xcode
npx cap open ios
```

4. **Opção B: Usar Cordova**

```bash
# Instalar Cordova
npm install -g cordova

# Criar projeto
cordova create SeuFuturoApp br.com.hypersecit.seufuturo 'SeuFuturo'

# Adicionar plataforma iOS
cordova platform add ios

# Compilar para iOS
cordova build ios
```

### Microsoft Store (Windows)

1. **Requisitos:**
   - Partner Center Account
   - Identidade de desenvolvedor (gratuita)

2. **Passo a passo:**

```bash
# Usar PWABuilder
npm install -g pwabuilder

# Gerar MSIX para Windows
pwabuilder build -p windows10
```

## 📦 Preparação do Projeto

### 1. Otimizar Ícones

Criar ícones em diferentes tamanhos:
- 48x48 px (favicon)
- 96x96 px (Android Chrome)
- 192x192 px (Android)
- 512x512 px (Android splash screen)
- 1024x1024 px (iOS)

**Ferramentas recomendadas:**
- https://www.favicon-generator.org/
- https://www.pwabuilder.com/ (gera automaticamente)

### 2. Testar PWA

```bash
# Servir localmente HTTPS (necessário para PWA)
python -m http.server 8000

# Acessar: https://localhost:8000
```

### 3. Validar com PWA Builder

Ir a: https://www.pwabuilder.com/

- Colar URL: `https://seufuturo.blog.br`
- Seguir recomendações
- Gerar apps para todas as plataformas

## 🚀 Passo a Passo Completo para Android

### 1. Preparar o Servidor

```bash
# Garantir HTTPS (obrigatório para PWA)
# Usar Let's Encrypt (gratuito)
# ou Cloudflare Pages

# Frontend deve estar em:
https://seufuturo.blog.br/
https://seufuturo.blog.br/manifest.json
https://seufuturo.blog.br/service-worker.js
```

### 2. Instalar Bubblewrap

```bash
# Node.js deve estar instalado (v14+)
npm install -g @bubblewrap/cli

# Verificar
bubblewrap --version
```

### 3. Gerar APK/AAB

```bash
# Navegar para pasta frontend
cd frontend

# Inicializar Bubblewrap
bubblewrap init --manifest manifest.json

# Será solicitado:
# - Package name: br.com.hypersecit.seufuturo
# - App name: SeuFuturo
# - Versão
# - Domínio da app

# Construir release
bubblewrap build --release --output-format aab
```

### 4. Publicar na Google Play Store

```bash
# Fazer login na Play Store
# 1. Acesso: https://play.google.com/apps/publish
# 2. Clicar em "Create app"
# 3. Preencher dados da app
# 4. Upload do AAB gerado
# 5. Preencher descrição, screenshots, política de privacidade
# 6. Enviar para revisão (leva 24-48h)
```

## 💻 Passo a Passo para iOS

### Opção 1: Usando PWABuilder (Mais Simples)

```bash
# Visitar: https://www.pwabuilder.com/

# 1. Colar URL da app
# 2. Clicar em "Package for stores"
# 3. Selecionar iOS
# 4. Download do projeto Xcode
# 5. Abrir em Xcode e publicar
```

### Opção 2: Usando Capacitor (Recomendado)

```bash
# 1. Instalar Capacitor
npm install @capacitor/core @capacitor/ios

# 2. Criar aplicativo iOS
npx cap init seufuturo 'br.com.hypersecit.seufuturo'

# 3. Copiar arquivos web
cp -r frontend/* www/

# 4. Adicionar iOS
npx cap add ios

# 5. Abrir Xcode
npx cap open ios

# 6. Assinar e configurar:
#    - Selecionar Team ID
#    - Configurar Bundle ID
#    - Selecionar simulator/device
#    - Build and Run

# 7. Enviar para TestFlight
#    - Abrir projeto em Xcode
#    - Product > Archive
#    - Validate App
#    - Distribute App
```

## 📱 Conteúdo Necessário para Publicação

### Descrição da App (250-280 caracteres)

**EN:**
"Discover daily horoscope predictions personalized for your zodiac sign. Get insights on love, career, and fortune with exclusive plans. Beautiful, responsive design. Available offline."

**PT:**
"Descobre previsões diárias de horóscopo personalizadas para o teu signo zodiacal. Obtém insights sobre amor, carreira e sorte com planos exclusivos. Design elegante e responsivo. Funciona offline."

### Keywords/Tags
- SeuFuturo
- Astrologia
- Previsões
- Zodíaco
- Daily Horoscope
- Astrology

### Screenshots Obrigatórios
- App launch screen
- Horoscope display
- Plans selection
- Testimonials

### Privacy Policy

```markdown
# Política de Privacidade - SeuFuturo

## Dados Coletados
- Signo zodiacal (armazenado localmente no navegador)
- Plano selecionado (localStorage)
- Nenhum dado pessoal é enviado para servidores

## Como Usamos Dados
- Melhorar a experiência do utilizador
- Análise de uso via Google Analytics (opcional)

## Direitos do Utilizador
- Direito ao esquecimento (limpar dados do navegador)
- Acesso aos dados pessoais

## Contacto
suporte@seufuturo.blog.br
```

### Terms of Service

```markdown
# Termos de Serviço - SeuFuturo

## Isenção de Responsabilidade
As previsões são para fins de entretenimento apenas.
Não devem ser usadas para tomar decisões importantes.

## Autorização de Uso
Ao usar o app, você concorda com estes termos.

## Propriedade Intelectual
Todos os direitos sobre conteúdo reservados.
```

## 🎨 Design Recomendado para Loja

### Dimensões de Screenshots (Google Play)
- **Telemóvel:** 1080 x 1920 px (até 8 imagens)
- **Tablet:** 1440 x 2560 px
- **Wear OS:** 540 x 540 px

### Banner de Feature
- Dimensões: 1024 x 500 px
- Formato: PNG/JPEG

### Ícone da App
- Dimensões: 512 x 512 px
- Sem cantos arredondados (a loja arredonda automaticamente)
- Sem transparência (fundo sólido)

## 🔐 Segurança

### HTTPS Obrigatório
```bash
# Usar Cloudflare (gratuito)
# 1. Adicionar domínio
# 2. Mudar nameservers
# 3. SSL ativado automaticamente

# ou Let's Encrypt
certbot certonly --standalone -d seu-dominio.com
```

### Assinatura Digital

#### Android:
```bash
# Gerar chave privada
keytool -genkey -v -keystore my-key.keystore \
  -keyalg RSA -keysize 2048 -validity 10000

# Assinar APK
jarsigner -verbose -sigalg SHA1withRSA \
  -digestalg SHA1 -keystore my-key.keystore \
  app-release-unsigned.apk alias_name
```

#### iOS:
- Feito automaticamente via Xcode
- Requer Certificate Apple Developer

## 📊 Analytics (Opcional)

Adicionar ao `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🚀 Deploy Recomendado

### Opção 1: Netlify (Recomendado para PWA)
```bash
npm install -g netlify-cli
cd frontend
netlify deploy --prod
```

### Opção 2: Vercel
```bash
npm install -g vercel
cd frontend
vercel --prod
```

### Opção 3: Cloudflare Pages
```bash
# Conectar repositório GitHub
# Configurar build: sem build necessário
# Publish directory: frontend
```

## ✅ Checklist de Publicação

- [ ] Domínio com HTTPS configurado
- [ ] manifest.json válido
- [ ] service-worker.js funcional
- [ ] Ícones em todos os tamanhos
- [ ] Offline funcional
- [ ] Performance otimizada (Lighthouse 90+)
- [ ] Política de Privacidade online
- [ ] Termos de Serviço online
- [ ] Descrição e keywords preparadas
- [ ] Screenshots prontos
- [ ] App testada em múltiplos dispositivos
- [ ] Assinatura digital configurada
- [ ] Analytics (se desejado)

## 💰 Custos Estimados

| Plataforma | Taxa Inicial | Taxa Anual | Descrição |
|-----------|-------------|-----------|----------|
| Google Play | $25 | Grátis | 30% comissão em vendas |
| Apple App Store | $99 | $99 | 30% comissão em vendas |
| Microsoft Store | Grátis | Grátis | 30% comissão em vendas |
| Huawei AppGallery | Grátis | Grátis | 15% comissão em vendas |

## 🆘 Troubleshooting

### PWA não aparece no Play Store
- ✅ Verificar manifest.json válido (use: https://web.dev/pwa-checklist/)
- ✅ Service Worker registado corretamente
- ✅ HTTPS ativo

### Build APK falha
```bash
# Limpar cache
bubblewrap update-wrapper
rm -rf app

# Tentar novamente
bubblewrap build --release
```

### iOS não instala no device
```bash
# No Xcode:
# 1. Product > Clean Build Folder
# 2. Select physical device
# 3. Product > Build
# 4. Product > Run
```

## 📚 Recursos Úteis

- **PWA Checklist:** https://web.dev/pwa-checklist/
- **PWABuilder:** https://www.pwabuilder.com/
- **Bubblewrap Docs:** https://github.com/GoogleChromeLabs/bubblewrap
- **Capacitor Docs:** https://capacitorjs.com/
- **Apple App Store Guidelines:** https://developer.apple.com/app-store/review/guidelines/
- **Google Play Policies:** https://play.google.com/about/developer-content-policy/

## 🎉 Próximas Etapas

1. ✅ Configurar domínio com HTTPS
2. ✅ Fazer deploy do frontend
3. ✅ Testar PWA localmente
4. ✅ Gerar builds para lojas
5. ✅ Criar contas developer
6. ✅ Preparar conteúdo de loja
7. ✅ Submeter para revisão
8. ✅ Publicado! 🎉

---

**Versão:** 1.0.0  
**Última atualização:** 17 de maio de 2026  
**Status:** Pronto para publicação em todas as lojas
