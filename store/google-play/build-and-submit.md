# Build e envio - Google Play

## Pre-requisitos

- Conta Google Play Console ativa.
- Android Studio ou JDK/Gradle funcionando.
- Package name: `br.blog.seufuturo`.
- Keystore de release guardada fora do repositorio.

## Preparar o projeto

```bash
npm install
npm run build:store
```

Abra no Android Studio, se quiser validar visualmente:

```bash
npm run android:open
```

## Assinatura de release

Crie uma keystore de release e copie `android/key.properties.example` para `android/key.properties`.

Exemplo de campos:

```properties
storeFile=C:\\Users\\Flavio\\secrets\\seufuturo-release.jks
storePassword=SUA_SENHA
keyAlias=seufuturo
keyPassword=SUA_SENHA
```

O arquivo `android/key.properties` e a keystore nao devem ser versionados.

## Gerar AAB

No Windows:

```bash
npm run android:bundle:win
```

Saida esperada:

```text
android/app/build/outputs/bundle/release/app-release.aab
```

Se o arquivo `android/key.properties` nao existir, o Gradle pode gerar uma variante sem assinatura de release. Para upload no Play Console, use AAB assinado.

Neste ambiente, o script Windows usa as ferramentas locais em `%LOCALAPPDATA%\SeuFuturoBuildTools` e a keystore em `%USERPROFILE%\secrets\seufuturo-release.jks`.

## Play Console

1. Crie o app como gratuito.
2. Preencha a ficha com `store/google-play/listing-pt-BR.md`.
3. Envie icone, feature graphic e screenshots.
4. Preencha Data Safety com `store/privacy/data-safety-and-app-privacy.md`.
5. Declare que nao ha anuncios, se nenhum SDK de anuncios for adicionado.
6. Envie o `.aab` para teste interno ou fechado.
7. Para conta pessoal criada depois de 13/11/2023, mantenha teste fechado com pelo menos 12 testers opt-in por 14 dias continuos.
8. Depois, solicite acesso a producao e envie para revisao.
