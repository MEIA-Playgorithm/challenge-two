# Backend

The backend is a Python API (application programming interface) for the Playgorithm coach management system. We build it with FastAPI, manage it with uv and check it with ruff.

## Run with Docker

From the repository root, run:

```bash
docker compose up -d --build backend
```

The API answers at [http://localhost:8000](http://localhost:8000). `GET /health` returns `{"status": "ok", "version": "0.1.0"}`. The interactive API documentation is at [http://localhost:8000/docs](http://localhost:8000/docs).

## Run on your computer

You need [uv](https://docs.astral.sh/uv/). uv installs Python 3.13 for you if you do not have it.

1. Go to the folder: `cd backend`
2. Install the dependencies: `uv sync`
3. Start the server with auto-reload: `uv run src/main.py --dev`

The server answers at [http://127.0.0.1:8000](http://127.0.0.1:8000). Auto-reload restarts the server when a file in `src/` changes. To start the server without auto-reload, run `uv run src/main.py`.

You can add these options to the command:

| Option | Default | Meaning |
|---|---|---|
| `--dev` | off | Restart the server when a file in `src/` changes |
| `--host` | `127.0.0.1` | Address the server listens on |
| `--port` | `8000` | Port the server listens on |

Docker does not use this script. It runs `uvicorn main:app --app-dir src --host 0.0.0.0`.

## Check the code

| Task | Command |
|---|---|
| Run the tests | `uv run pytest` |
| Find lint errors | `uv run ruff check .` |
| Fix the formatting | `uv run ruff format .` |

## Configure the backend

The backend reads these environment variables when it starts:

| Variable | Default | Meaning |
|---|---|---|
| `APP_NAME` | `Playgorithm` | Name shown in the API documentation |
| `APP_VERSION` | `0.1.0` | Version returned by `/health` |
| `CORS_ORIGINS` | `http://localhost:4173,http://localhost:5173` | Comma-separated addresses that may call the API from a browser |

CORS (cross-origin resource sharing) lets the frontend, which runs on another port, call the API.

## Code organisation

We split the code into layers. Each layer calls only the layers below it.

```
src/
  main.py           builds every object by hand and connects the layers
  api/routes/       HTTP routes: translate requests into service calls
  api/schemas/      request and response models (Pydantic)
  services/         business rules, predictions and decisions
  repositories/     read and write data: CSV files, trained models
  domain/           plain data classes, with no imports from other layers
  core/             settings shared by every layer
tests/              tests run with pytest
```

Rules for the code:

- Keep the code plain: no metaclasses, no `setattr` or `getattr` tricks, no dynamic imports and no monkey patching.
- Pass each dependency in the constructor. `main.py` creates every object, so you can read the whole wiring in one file.
- Keep FastAPI in the `api` layer and in `main.py` only.
- Give every route a response schema, and convert domain objects to schemas with a plain function.
- Import from the layer packages directly, for example `from services.health_service import HealthService`. The `src` folder is on the Python path, so never write `from src.`.
