#!/usr/bin/env bash
# setup.sh — Post-create verification for the Manim Dev Container
# Checks that manim, ffmpeg, and latex are installed and on the PATH.

set -euo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No colour

PASS=0
FAIL=0

check() {
  local label="$1"
  local cmd="$2"

  if eval "$cmd" &>/dev/null; then
    echo -e "  ${GREEN}✔${NC}  ${label}"
    PASS=$((PASS + 1))
  else
    echo -e "  ${RED}✘${NC}  ${label}  ${YELLOW}(not found or errored)${NC}"
    FAIL=$((FAIL + 1))
  fi
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Manim Dev Container — Environment Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Python ─────────────────────────────────────────────────────────────────────
echo "Python:"
check "python3 in PATH"          "command -v python3"
check "pip in PATH"              "command -v pip"
check "python3 --version"        "python3 --version"

# ── Manim ──────────────────────────────────────────────────────────────────────
echo ""
echo "Manim:"
check "manim in PATH"            "command -v manim"
check "manim --version"          "manim --version"
check "manim importable"         "python3 -c 'import manim'"

# ── FFmpeg ─────────────────────────────────────────────────────────────────────
echo ""
echo "FFmpeg:"
check "ffmpeg in PATH"           "command -v ffmpeg"
check "ffmpeg -version"          "ffmpeg -version"

# ── LaTeX / dvisvgm ────────────────────────────────────────────────────────────
echo ""
echo "LaTeX:"
check "latex in PATH"            "command -v latex"
check "pdflatex in PATH"         "command -v pdflatex"
check "dvisvgm in PATH"          "command -v dvisvgm"
check "latex --version"          "latex --version"

# ── Cairo / Pango (native libs) ────────────────────────────────────────────────
echo ""
echo "Native libraries:"
check "pkg-config available"     "command -v pkg-config"
check "cairo pkg-config entry"   "pkg-config --exists cairo"
check "pango pkg-config entry"   "pkg-config --exists pango"

# ── Jupyter ────────────────────────────────────────────────────────────────────
echo ""
echo "Jupyter:"
check "jupyter in PATH"          "command -v jupyter"
check "jupyterlab importable"    "python3 -c 'import jupyterlab'"

# ── NumPy ──────────────────────────────────────────────────────────────────────
echo ""
echo "Python packages:"
check "numpy importable"         "python3 -c 'import numpy'"

# ── Summary ────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Results: ${GREEN}${PASS} passed${NC}  /  ${RED}${FAIL} failed${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$FAIL" -gt 0 ]; then
  echo -e "${RED}Some checks failed. Review the output above.${NC}"
  exit 1
else
  echo -e "${GREEN}All checks passed — environment is ready!${NC}"
fi
