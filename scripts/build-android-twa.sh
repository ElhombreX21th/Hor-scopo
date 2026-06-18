#!/usr/bin/env bash
set -euo pipefail

APP_URL="${APP_URL:-https://seufuturo.blog.br}"
MANIFEST_URL="${MANIFEST_URL:-https://seufuturo.blog.br/manifest.json}"
PACKAGE_ID="${PACKAGE_ID:-br.com.hypersecit.seufuturo}"
APP_NAME="${APP_NAME:-SeuFuturo}"
OUT_DIR="${OUT_DIR:-android-twa-build}"

printf '\n== SeuFuturo Android TWA Build ==\n'
printf 'App URL: %s\n' "$APP_URL"
printf 'Manifest URL: %s\n' "$MANIFEST_URL"
printf 'Package ID: %s\n' "$PACKAGE_ID"
printf 'Output dir: %s\n\n' "$OUT_DIR"

command -v node >/dev/null 2>&1 || { echo "Node.js não encontrado."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm não encontrado."; exit 1; }
command -v java >/dev/null 2>&1 || { echo "Java/JDK não encontrado."; exit 1; }

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

cat <<'MSG'
Este script prepara o build Android via Bubblewrap.
Durante a primeira execução, responda aos prompts usando:
- Package ID: br.com.hypersecit.seufuturo
- App name: SeuFuturo
- Host/domain: seufuturo.blog.br
- Start URL: /
- Display mode: standalone/fullscreen quando solicitado
- Output format: Android App Bundle (.aab)

IMPORTANTE: salve a keystore e as senhas. Elas serão necessárias para atualizações futuras.
MSG

npx --yes @bubblewrap/cli init --manifest "$MANIFEST_URL" --directory "$OUT_DIR"
cd "$OUT_DIR"
npx --yes @bubblewrap/cli build

printf '\nBuild finalizado. Procure o arquivo .aab dentro de: %s\n' "$OUT_DIR"
printf 'Depois gere/atualize assetlinks.json com a impressão SHA-256 da assinatura do app.\n'
