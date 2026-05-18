#!/usr/bin/env bash
set -euo pipefail

# deploy_remote.sh
# Uso: ./deploy_remote.sh user@host /opt/seufuturo main /path/to/.env
# Envia um tarball do branch especificado para o host remoto e executa deploy/deploy.sh

SSH_TARGET="${1:?Provide SSH target (user@host)}"
TARGET_DIR="${2:-/opt/seufuturo}"
BRANCH="${3:-main}"
ENV_PATH="${4:-}" # path to local .env to upload (optional)

TARBALL="/tmp/seufuturo_${BRANCH}_$(date +%s).tar.gz"

echo "Criando tarball do branch $BRANCH -> $TARBALL"
git rev-parse --verify "$BRANCH" >/dev/null 2>&1 || { echo "Branch $BRANCH não encontrado" >&2; exit 1; }
git archive --format=tar "$BRANCH" | gzip > "$TARBALL"

echo "Enviando tarball para $SSH_TARGET:/tmp/"
scp "$TARBALL" "$SSH_TARGET:/tmp/" || { echo "Falha no scp" >&2; rm -f "$TARBALL"; exit 1; }

echo "Extraindo em $SSH_TARGET:$TARGET_DIR"
ssh "$SSH_TARGET" bash -c "'
  set -euo pipefail
  mkdir -p $TARGET_DIR
  tar -xzf /tmp/$(basename "$TARBALL") -C $TARGET_DIR
  chown -R $(whoami):$(whoami) $TARGET_DIR || true
  if [ -f $TARGET_DIR/deploy/deploy.sh ]; then
    chmod +x $TARGET_DIR/deploy/deploy.sh
  fi
'" || { echo "Falha ao extrair remoto" >&2; rm -f "$TARBALL"; exit 1; }

if [ -n "$ENV_PATH" ] && [ -f "$ENV_PATH" ]; then
  echo "Enviando .env para $SSH_TARGET:$TARGET_DIR/.env"
  scp "$ENV_PATH" "$SSH_TARGET:$TARGET_DIR/.env" || echo "Aviso: falha ao enviar .env"
fi

echo "Executando deploy remoto via deploy/deploy.sh (padrão)"
ssh "$SSH_TARGET" bash -lc "'
  set -euo pipefail
  cd $TARGET_DIR
  if [ -f deploy/deploy.sh ]; then
    chmod +x deploy/deploy.sh
    ./deploy/deploy.sh $TARGET_DIR $BRANCH
  else
    echo "deploy/deploy.sh não encontrado em $TARGET_DIR" >&2
    exit 1
  fi
'"

echo "Limpando tarball local"
rm -f "$TARBALL"

echo "Deploy remoto concluído. Verifique logs e containers no host remoto."
