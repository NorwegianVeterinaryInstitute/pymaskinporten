# syntax=docker/dockerfile:1

# Define Python version as an argument
ARG PYTHON_VERSION=3.13

## Builder image with python and uv
FROM python:${PYTHON_VERSION}-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN <<EOF
    uv --version
    python --version
EOF

ENV \
    UV_CACHE_DIR=/cache \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LOCKED=1 \
    UV_PROJECT_ENVIRONMENT=/app

WORKDIR /src
# 2-step install, first dependencies, then the project itself
#
# `UV_LOCKED=1` - makes sure the uv.lock file is in sync with `pyproject.toml`
# `UV_PROJECT_ENVIRONMENT=/app` - installs into non-venv structure in /app

# Install dependencies in their own layer
RUN --mount=type=cache,target=/cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-dev --no-editable --no-install-project --extra web

# Copy the project into the builder - COPY is affected by `.dockerignore`
COPY . /src

# Sync the project - it will be installed in /app/
RUN --mount=type=cache,target=/cache \
    uv sync --no-dev --no-editable --extra web


## Runtime image
FROM python:${PYTHON_VERSION}-slim

# remove debianisms not needed in application containers
RUN rm -rf /media /mnt /boot /home /opt /srv /var

COPY --from=builder /app/ /app/

ENV PATH=/app/bin:$PATH
# Listen on all interfaces inside the container; publish to 127.0.0.1 on the host
ENV FLASK_RUN_HOST=0.0.0.0

ENTRYPOINT ["maskinporten-web"]