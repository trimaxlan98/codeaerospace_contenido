# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.12-slim-bullseye

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── System dependencies ────────────────────────────────────────────────────────
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
