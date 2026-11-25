FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

COPY . .
RUN uv sync --locked --no-dev

CMD [".venv/bin/uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
