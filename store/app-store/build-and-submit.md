# Build e envio - App Store

## Pre-requisitos

- Conta Apple Developer Program ativa.
- Acesso ao App Store Connect.
- Mac com Xcode instalado.
- Bundle ID: `br.blog.seufuturo`.

## Preparar o projeto

No repositorio:

```bash
npm install
npm run build:store
```

Leve a pasta do projeto para um Mac e abra:

```bash
npm run ios:open
```

Ou abra diretamente:

```bash
open ios/App/App.xcworkspace
```

## Xcode

1. Selecione o target `App`.
2. Em Signing & Capabilities, selecione a equipe Apple.
3. Confirme Bundle Identifier `br.blog.seufuturo`.
4. Confirme Version `1.0` e Build `1`.
5. Use um dispositivo generico iOS para Archive.
6. Menu Product > Archive.
7. No Organizer, valide e distribua para App Store Connect.

## App Store Connect

1. Crie o app record em Apps > New App.
2. Use nome `SeuFuturo`, bundle `br.blog.seufuturo` e idioma `pt-BR`.
3. Preencha a ficha com `store/app-store/listing-pt-BR.md`.
4. Envie o icone `store/assets/app-icon-1024.png`.
5. Envie os screenshots de `store/screenshots/app-store/`.
6. Preencha App Privacy com `store/privacy/data-safety-and-app-privacy.md`.
7. Selecione o build depois do processamento.
8. Envie para App Review.

## Notas de revisao

Use a nota em `store/app-store/listing-pt-BR.md`. A primeira versao e gratuita e nao exibe compra externa no app nativo.
