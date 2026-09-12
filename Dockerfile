# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bullseye

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── System dependencies ────────────────────────────────────────────────────────
# Bullseye llego a su fin de vida: deb.debian.org ya no sirve sus paquetes
# (404 en todo bullseye-security) y su Release vencio el 2026-09-07, asi que
# `apt-get update` abortaba con exit 100 y la imagen de render no se podia
# reconstruir. Se apunta al archivo historico, que si los tiene.
#
# NO se sube la base a bookworm A PROPOSITO: cambiar la distribucion cambia
# Pango y las fuentes del sistema, y con ellas las medidas tipograficas sobre
# las que estan calibrados los guardianes de lienzo.py y los 33 cursos ya
# publicados. Esta imagen tiene que medir manana lo mismo que midio ayer.
RUN set -eux; \
    printf '%s\n%s\n%s\n' \
      'deb http://snapshot.debian.org/archive/debian/20250721T000000Z bullseye main' \
      'deb http://snapshot.debian.org/archive/debian-security/20250721T000000Z bullseye-security main' \
      'deb http://snapshot.debian.org/archive/debian/20250721T000000Z bullseye-updates main' \
      > /etc/apt/sources.list; \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Video rendering
    ffmpeg \
    # Text layout (Pango)
    libpango1.0-dev \
    # LaTeX suite for equation rendering
    texlive \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-latex-recommended \
    dvisvgm \
    # Cairo / pkg-config (required by pycairo / manim)
    pkg-config \
    libcairo2-dev \
    # OpenGL headless (Mesa/EGL): permite --renderer=opengl sin GPU/display
    libgl1-mesa-glx \
    libegl1-mesa \
    libglu1-mesa \
    # Build utilities
    build-essential \
    git \
    curl \
    # Clean up apt caches
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ────────────────────────────────────────────────────────
WORKDIR /workspace

COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Default command ────────────────────────────────────────────────────────────
CMD ["bash"]
