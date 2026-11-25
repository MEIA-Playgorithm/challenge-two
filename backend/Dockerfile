FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

COPY . .
RUN uv sync --locked --no-dev

ENV APP_HOST=0.0.0.0

CMD [".venv/bin/python", "src/main.py"]
