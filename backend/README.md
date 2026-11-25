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

The script has one option:

| Option | Default | Meaning |
|---|---|---|
| `--dev` | off | Restart the server when a file in `src/` changes |

The script reads the host and port from the settings. To change them, set `APP_HOST` and `APP_PORT`. See [Configure the backend](#configure-the-backend).

In dev mode, the script gives uvicorn the name `"main:app"`, because uvicorn reloads only an app that it imports by name. Without `--dev`, the script gives uvicorn the app object.

Docker runs the same script: `python src/main.py`. The Dockerfile sets `APP_HOST=0.0.0.0`, so the API is reachable from outside the container.

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
| `APP_HOST` | `127.0.0.1` | Address the server listens on |
| `APP_PORT` | `8000` | Port the server listens on |

CORS (cross-origin resource sharing) lets the frontend, which runs on another port, call the API.

### Use a `.env` file

You can set these variables in `backend/.env`:

1. Go to the folder: `cd backend`
2. Copy the example file: `cp .env.example .env` (on Windows PowerShell: `Copy-Item .env.example .env`)
3. Edit `.env` with your values.

`src/main.py` loads the file with python-dotenv when it starts. A variable that is already set in the environment wins over the same variable in `.env`. The file is optional, and the defaults in the table apply when a variable is missing.

Docker Compose also passes `backend/.env` to the container when the file exists. Compose starts without it. Do not commit `.env`. The `.env.example` file is safe to commit.

## Code organisation

We split the code into layers. Each layer calls only the layers below it.

```
src/
  app.py            composition root: create_app(settings) builds the app and every object by hand, and connects the layers
  main.py           command-line entry point: creates the app instance with create_app and starts uvicorn
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
- Pass each dependency in the constructor. `create_app` in `app.py` creates every object, so you can read the whole wiring in one function. `main.py` calls it once to create the app instance.
- Keep FastAPI in the `api` layer and in `app.py` only.
- Build the app in tests with `create_app(settings)` from `app`, not with the `app` instance in `main`.
- Give every route a response schema, and convert domain objects to schemas with a plain function.
- Import from the layer packages directly, for example `from services.health_service import HealthService`. The `src` folder is on the Python path, so never write `from src.`.
