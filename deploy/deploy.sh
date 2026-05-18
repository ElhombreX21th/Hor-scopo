#!/usr/bin/env bash
set -euo pipefail

# Deploy script para servidor (rodar no servidor ou via SSH)
# Uso: ./deploy.sh /opt/seufuturo main

TARGET_DIR="${1:-/opt/seufuturo}"
BRANCH="${2:-main}"

REPO_URL="$(git config --get remote.origin.url || true)"
if [ -z "$REPO_URL" ]; then
  echo "Não foi possível detectar a URL do repositório. Execute este script a partir de um clone do repo ou exporte REPO_URL." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker não encontrado. Instale Docker no servidor antes de prosseguir." >&2
  exit 1
fi

COMPOSE_CMD=""
if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  echo "docker-compose não encontrado. Instale docker-compose ou use Docker Compose v2 (docker compose)." >&2
  exit 1
fi

echo "Deploy: repositório=$REPO_URL dir=$TARGET_DIR branch=$BRANCH"

mkdir -p "$TARGET_DIR"

if [ -d "$TARGET_DIR/.git" ]; then
  echo "Atualizando repositório existente em $TARGET_DIR"
  cd "$TARGET_DIR"
  git fetch --all --prune
  git checkout "$BRANCH"
  git reset --hard "origin/$BRANCH"
else
  echo "Clonando repositório em $TARGET_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
  cd "$TARGET_DIR"
fi

echo "Construindo e subindo containers com $COMPOSE_CMD"
$COMPOSE_CMD pull || true
$COMPOSE_CMD build --pull
$COMPOSE_CMD up -d --remove-orphans

echo "Containers ativos:"
$COMPOSE_CMD ps

# systemd service installation (opcional)
if [ -f deploy/seufuturo.service ]; then
  if [ "$EUID" -ne 0 ]; then
    echo "Para instalar o systemd unit execute como root (ex: sudo):"
    echo "  sudo cp deploy/seufuturo.service /etc/systemd/system/seufuturo.service"
    echo "  sudo systemctl daemon-reload && sudo systemctl enable --now seufuturo"
  else
    cp deploy/seufuturo.service /etc/systemd/system/seufuturo.service
    systemctl daemon-reload
    systemctl enable --now seufuturo
    echo "systemd unit instalado e iniciado"
  fi
fi

echo "Deploy concluído. Revise logs e variáveis de ambiente (.env)."
