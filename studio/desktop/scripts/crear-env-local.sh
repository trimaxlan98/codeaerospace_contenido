#!/usr/bin/env bash
# crear-env-local.sh — studio/backend/.env para correr ManimStudio en local.
#
# El .env.example es el del VPS (rutas /var/www, /run/manimstudio, cookie
# Secure). En local hace falta otro: workspace y socket dentro del checkout y
# cookie sin Secure (http://127.0.0.1). Este script lo genera con un secreto
# aleatorio y el hash bcrypt de la contraseña elegida. NO sobrescribe un .env
# existente.
#
#   CODE_STUDIO_PASSWORD='...' bash studio/desktop/scripts/crear-env-local.sh
#   bash studio/desktop/scripts/crear-env-local.sh        (la pide por teclado)
#
# Requiere studio/backend/venv (usa su bcrypt).

set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ENV="$REPO/studio/backend/.env"
PY="$REPO/studio/backend/venv/bin/python"

[[ -f "$ENV" ]] && { echo "ya existe $ENV; no se toca"; exit 0; }
[[ -x "$PY" ]] || { echo "falta studio/backend/venv"; exit 1; }

PASS="${CODE_STUDIO_PASSWORD:-}"
if [[ -z "$PASS" ]]; then
  read -r -s -p "Contraseña para entrar al Estudio local: " PASS; echo
fi
[[ ${#PASS} -ge 8 ]] || { echo "la contraseña debe tener al menos 8 caracteres"; exit 1; }

HASH="$(CODE_STUDIO_PASSWORD="$PASS" "$PY" -c 'import bcrypt,os; print(bcrypt.hashpw(os.environ["CODE_STUDIO_PASSWORD"].encode(), bcrypt.gensalt(12)).decode())')"
SECRET="$("$PY" -c 'import secrets; print(secrets.token_urlsafe(48))')"

umask 077
cat > "$ENV" <<EOF
# ManimStudio — entorno LOCAL (generado por studio/desktop/scripts/crear-env-local.sh).
# Ignorado por git. No es el .env del VPS.
MS_ADMIN_USER=admin
# Comillas simples: el hash lleva \$ y bash lo expandiria al hacer \`source .env\`
MS_ADMIN_PASSWORD_HASH='$HASH'
MS_SECRET_KEY='$SECRET'

MS_WORKSPACE=$REPO
MS_DB_PATH=$REPO/studio/backend/manimstudio.db
MS_RUNNER_SOCKET=$REPO/.run/runner.sock

# http://127.0.0.1 sin TLS -> la cookie de sesion no puede ser Secure
MS_COOKIE_SECURE=0
MS_MAX_STORAGE_MB=20480
EOF
echo "creado $ENV (usuario: admin)"
