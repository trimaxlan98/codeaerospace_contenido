#!/usr/bin/env bash
# install-linux.sh — compila e instala CO.DE Studio para el usuario actual.
#
#   bash studio/desktop/scripts/install-linux.sh             compilar + instalar
#   bash studio/desktop/scripts/install-linux.sh --no-build  reinstalar el ultimo build
#   sudo bash studio/desktop/scripts/install-linux.sh --apparmor
#                                                            (opcional) perfil de AppArmor
#
# Instala en ~/.local/opt/code-studio, sin sudo. Deja:
#   ~/.local/bin/code-studio                     lanzador
#   ~/.local/share/applications/code-studio.desktop
#   ~/.local/share/icons/hicolor/*/apps/code-studio.png
#   <Escritorio>/code-studio.desktop             acceso directo
#
# Sobre el sandbox: Ubuntu 24.04+ restringe los user namespaces sin
# privilegios (kernel.apparmor_restrict_unprivileged_userns=1) y Chromium no
# puede montar su sandbox. El lanzador usa --no-sandbox en ese caso, como hace
# el AppImage de electron-builder. Con --apparmor se instala un perfil que le
# concede `userns` solo a este binario y el sandbox vuelve a estar activo.

set -euo pipefail

DESKTOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$DESKTOP_DIR/../.." && pwd)"
TARGET_USER="${SUDO_USER:-$USER}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
OPT="$TARGET_HOME/.local/opt/code-studio"
BIN="$TARGET_HOME/.local/bin/code-studio"
APPS="$TARGET_HOME/.local/share/applications"
ICONS="$TARGET_HOME/.local/share/icons/hicolor"
PROFILE=/etc/apparmor.d/code-studio

if [[ "${1:-}" == "--apparmor" ]]; then
  [[ $EUID -eq 0 ]] || { echo "--apparmor necesita sudo"; exit 1; }
  cat > "$PROFILE" <<EOF
# CO.DE Studio (Electron): permite user namespaces para el sandbox de Chromium.
abi <abi/4.0>,
include <tunables/global>

profile code-studio $OPT/code-studio flags=(unconfined) {
  userns,
  include if exists <local/code-studio>
}
EOF
  apparmor_parser -r "$PROFILE"
  echo "perfil AppArmor instalado: $PROFILE (el lanzador ya no usara --no-sandbox)"
  exit 0
fi

[[ $EUID -ne 0 ]] || { echo "no ejecutes la instalacion con sudo (solo --apparmor)"; exit 1; }

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }

if [[ "${1:-}" != "--no-build" ]]; then
  cd "$DESKTOP_DIR"
  step "dependencias de la app"
  [[ -d node_modules/electron/dist ]] || { npm ci --no-audit --no-fund && npm approve-scripts electron >/dev/null 2>&1 || true; node node_modules/electron/install.js; }
  step "iconos"
  node scripts/make-icons.mjs
  step "pruebas"
  npm test --silent
  step "empaquetando (electron-builder --linux dir)"
  npx electron-builder --linux dir
fi

# La interfaz del Estudio que sirve la app es studio/frontend/dist: si falta
# o es mas vieja que su codigo, se compila aqui para que el primer arranque
# no enseñe una version antigua.
FRONT="$REPO/studio/frontend"
if [[ ! -f "$FRONT/dist/index.html" ]] || [[ -n "$(find "$FRONT/src" "$FRONT/index.html" -newer "$FRONT/dist/index.html" -print -quit)" ]]; then
  step "compilando la interfaz del Estudio (studio/frontend)"
  (cd "$FRONT" && { [[ -d node_modules ]] || npm ci --no-audit --no-fund; } && npm run build)
fi

step "instalando en $OPT"
mkdir -p "$OPT" "$(dirname "$BIN")" "$APPS"
rsync -a --delete "$DESKTOP_DIR/release/linux-unpacked/" "$OPT/"

for size in 16 24 32 48 64 128 256 512; do
  mkdir -p "$ICONS/${size}x${size}/apps"
  cp "$DESKTOP_DIR/build/icons/${size}x${size}.png" "$ICONS/${size}x${size}/apps/code-studio.png"
done
gtk-update-icon-cache -q -t "$ICONS" 2>/dev/null || true

cat > "$BIN" <<EOF
#!/usr/bin/env bash
# Lanzador de CO.DE Studio (generado por install-linux.sh).
export CHROME_DESKTOP=code-studio.desktop
FLAGS=()
if [[ "\$(cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns 2>/dev/null)" == "1" && ! -f $PROFILE ]]; then
  FLAGS+=(--no-sandbox)
fi
exec "$OPT/code-studio" "\${FLAGS[@]}" "\$@"
EOF
chmod +x "$BIN"

DESKTOP_ENTRY="[Desktop Entry]
Type=Application
Name=CO.DE Studio
GenericName=Estudio de video Manim
Comment=ManimStudio local: estudio, exports por tema y terminal con Claude Code
Exec=$BIN %U
Icon=code-studio
Terminal=false
Categories=AudioVideo;Video;Development;Education;
Keywords=manim;video;curso;claude;render;
StartupWMClass=code-studio
StartupNotify=true"
echo "$DESKTOP_ENTRY" > "$APPS/code-studio.desktop"
update-desktop-database -q "$APPS" 2>/dev/null || true

ESCRITORIO="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$TARGET_HOME/Desktop")"
if [[ -d "$ESCRITORIO" ]]; then
  echo "$DESKTOP_ENTRY" > "$ESCRITORIO/code-studio.desktop"
  chmod +x "$ESCRITORIO/code-studio.desktop"
  # GNOME solo lanza accesos directos del escritorio marcados como confiables.
  gio set "$ESCRITORIO/code-studio.desktop" metadata::trusted true 2>/dev/null || true
fi

# Primer arranque sin preguntar: se apunta la app a este checkout.
CFG_DIR="$TARGET_HOME/.config/CO.DE Studio"
if [[ ! -f "$CFG_DIR/config.json" ]]; then
  mkdir -p "$CFG_DIR"
  printf '{\n  "repoPath": "%s"\n}\n' "$REPO" > "$CFG_DIR/config.json"
fi

step "listo"
echo "  app:        $OPT"
echo "  lanzador:   $BIN"
echo "  escritorio: $ESCRITORIO/code-studio.desktop"
echo "  repo:       $REPO"
if [[ "$(cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns 2>/dev/null)" == "1" && ! -f $PROFILE ]]; then
  echo
  echo "  Nota: arrancara con --no-sandbox (AppArmor restringe user namespaces)."
  echo "  Para activar el sandbox:  sudo bash $DESKTOP_DIR/scripts/install-linux.sh --apparmor"
fi
