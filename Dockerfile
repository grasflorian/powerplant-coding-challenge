FROM python:3.13-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Install the project into `/app`
WORKDIR /app


# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project  --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev
RUN uv pip install .

FROM python:3.13-slim-trixie
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Setup a non-root user
RUN groupadd --system --gid 999 powerplantapp \
 && useradd --system --gid 999 --uid 999 --create-home powerplantapp

USER nonroot
# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

CMD ["serve"]